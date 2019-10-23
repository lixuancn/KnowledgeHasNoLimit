package cron

import (
	"context"
	"sort"
	"sync"
	"time"
)

// Cron keeps track of any number of entries, invoking the associated func as
// specified by the schedule. It may be started, stopped, and the entries may
// be inspected while running.
type Cron struct {
	entries   []*Entry
	chain     Chain
	stop      chan struct{}
	add       chan *Entry
	remove    chan EntryID
	snapshot  chan chan []Entry
	running   bool
	logger    Logger
	runningMu sync.Mutex
	location  *time.Location
	parser    Parser
	nextID    EntryID
	jobWaiter sync.WaitGroup
}

// Job is an interface for submitted cron jobs.
type Job interface {
	Run()
}

// Schedule describes a job's duty cycle.
type Schedule interface {
	// Next returns the next activation time, later than the given time.
	// Next is invoked initially, and then each time the job is run.
	Next(time.Time) time.Time
}

// EntryID identifies an entry within a Cron instance
type EntryID int

// Entry consists of a schedule and the func to execute on that schedule.
type Entry struct {
	// ID is the cron-assigned ID of this entry, which may be used to look up a
	// snapshot or remove it.
	ID EntryID

	// Schedule on which this job should be run.
	Schedule Schedule

	// Next time the job will run, or the zero time if Cron has not been
	// started or this entry's schedule is unsatisfiable
	Next time.Time

	// Prev is the last time this job was run, or the zero time if never.
	Prev time.Time

	// WrappedJob is the thing to run when the Schedule is activated.
	WrappedJob Job

	// Job is the thing that was submitted to cron.
	// It is kept around so that user code that needs to get at the job later,
	// e.g. via Entries() can do so.
	Job Job
}

// Valid returns true if this is not the zero entry.
func (e Entry) Valid() bool { return e.ID != 0 }

// byTime is a wrapper for sorting the entry array by time
// (with zero time at the end).
type byTime []*Entry

func (s byTime) Len() int      { return len(s) }
func (s byTime) Swap(i, j int) { s[i], s[j] = s[j], s[i] }
func (s byTime) Less(i, j int) bool {
	// Two zero times should return false.
	// Otherwise, zero is "greater" than any other time.
	// (To sort it at the end of the list.)
	if s[i].Next.IsZero() {
		return false
	}
	if s[j].Next.IsZero() {
		return true
	}
	return s[i].Next.Before(s[j].Next)
}

// New returns a new Cron job runner, modified by the given options.
//
// Available Settings
//
//   Time Zone
//     Description: The time zone in which schedules are interpreted
//     Default:     time.Local
//
//   Parser
//     Description: Parser converts cron spec strings into cron.Schedules.
//     Default:     Accepts this spec: https://en.wikipedia.org/wiki/Cron
//
//   Chain
//     Description: Wrap submitted jobs to customize behavior.
//     Default:     A chain that recovers panics and logs them to stderr.
//
// See "cron.With*" to modify the default behavior.
func New(opts ...Option) *Cron {
	c := &Cron{
		entries:   nil,
		chain:     NewChain(),
		add:       make(chan *Entry),
		stop:      make(chan struct{}),
		snapshot:  make(chan chan []Entry),
		remove:    make(chan EntryID),
		running:   false,
		runningMu: sync.Mutex{},
		logger:    DefaultLogger,
		location:  time.Local,
		parser:    standardParser,
	}
	for _, opt := range opts {
		opt(c)
	}
	return c
}

// FuncJob is a wrapper that turns a func() into a cron.Job
type FuncJob func()

func (f FuncJob) Run() { f() }

// AddFunc adds a func to the Cron to be run on the given schedule.
// The spec is parsed using the time zone of this Cron instance as the default.
// An opaque ID is returned that can be used to later remove it.
func (c *Cron) AddFunc(spec string, cmd func()) (EntryID, error) {
	return c.AddJob(spec, FuncJob(cmd))
}

// AddJob adds a Job to the Cron to be run on the given schedule.
// The spec is parsed using the time zone of this Cron instance as the default.
// An opaque ID is returned that can be used to later remove it.
func (c *Cron) AddJob(spec string, cmd Job) (EntryID, error) {
	schedule, err := c.parser.Parse(spec)
	if err != nil {
		return 0, err
	}
	return c.Schedule(schedule, cmd), nil
}

func (c *Cron)Schedule(schedule Schedule, cmd Job)EntryID{
	c.runningMu.Lock()
	defer c.runningMu.Unlock()
	c.nextID++
	entry := &Entry{
		ID: c.nextID,
		Schedule: schedule,
		WrappedJob: c.chain.Then(cmd),
		Job: cmd,
	}
	if !c.running{
		c.entries = append(c.entries, entry)
	}else{
		c.add <- entry
	}
	return entry.ID
}

func (c *Cron)Location()*time.Location{
	return c.location
}

func (c *Cron)now()time.Time{
	return time.Now().In(c.location)
}

//返回列表
func (c *Cron)Entries()[]Entry{
	c.runningMu.Lock()
	defer c.runningMu.Unlock()
	if c.running{
		replyChan := make(chan []Entry, 1)
		c.snapshot <- replyChan
		return <-replyChan
	}
	return c.entrySnapshot()
}

func (c *Cron)entrySnapshot()[]Entry{
	var entries = make([]Entry, len(c.entries))
	for i, e := range c.entries{
		entries[i] = *e
	}
	return entries
}

//根据id获取其中一个
func (c *Cron)Entry(id EntryID)Entry{
	for _, e := range c.Entries(){
		if id == e.ID{
			return e
		}
	}
	return Entry{}
}

func (c *Cron)Remove(id EntryID){
	c.runningMu.Lock()
	defer c.runningMu.Unlock()
	if c.running{
		c.remove <- id
	}else{
		c.removeEntry(id)
	}
}

func (c *Cron)removeEntry(id EntryID){
	var entries []*Entry
	for _, e := range c.entries{
		if e.ID != id{
			entries = append(entries, e)
		}
	}
	c.entries = entries
}

func (c *Cron)Start(){
	c.runningMu.Lock()
	defer c.runningMu.Unlock()
	if c.running{
		return
	}
	c.running = true
	go c.run()
}

func (c *Cron)Run(){
	c.runningMu.Lock()
	if c.running{
		c.runningMu.Unlock()
		return
	}
	c.running = true
	c.runningMu.Unlock()
	c.run()
}

func (c *Cron)run(){
	c.logger.Info("start")
	now := c.now()
	for _, e := range c.entries{
		e.Next = e.Schedule.Next(now)
		c.logger.Info("schedule", "now", now, "entry", e.ID, "next", e.Next)
	}
	for{
		sort.Sort(byTime(c.entries))
		var timer *time.Timer
		if len(c.entries) == 0 || c.entries[0].Next.IsZero(){
			timer = time.NewTimer(10000 * time.Hour)
		}else{
			timer = time.NewTimer(c.entries[0].Next.Sub(now))
		}
		for {
			select{
			case now = <- timer.C:
				now = now.In(c.location)
				c.logger.Info("wake", "now", now)
				for _, e := range c.entries{
					if e.Next.After(now) || e.Next.IsZero(){
						break
					}
					c.startJob(e.WrappedJob)
					e.Prev = e.Next
					e.Next = e.Schedule.Next(now)
					c.logger.Info("run", "now", now, "entry", e.ID, "next", e.Next)
				}
			case newEntry := <- c.add:
				timer.Stop()
				now = c.now()
				newEntry.Next = newEntry.Schedule.Next(now)
				c.entries = append(c.entries, newEntry)
				c.logger.Info("added", "now", now, "entry", newEntry.ID, "next", newEntry.Next)
			case <- c.stop:
				timer.Stop()
				c.logger.Info("stop")
				return
			case replyChan := <- c.snapshot:
				replyChan <- c.entrySnapshot()
				continue
			case id := <- c.remove:
				timer.Stop()
				now = c.now()
				c.removeEntry(id)
				c.logger.Info("removed", "entry", id)
			}
			break
		}
	}
}

func (c *Cron)startJob(j Job){
	c.jobWaiter.Add(1)
	go func(){
		defer c.jobWaiter.Done()
		j.Run()
	}()
}

func (c *Cron)Stop()context.Context{
	c.runningMu.Lock()
	defer c.runningMu.Unlock()
	if c.running {
		c.stop <- struct{}{}
		c.running = false
	}
	ctx, cancel := context.WithCancel(context.Background())
	go func(){
		c.jobWaiter.Wait()
		cancel()
	}()
	return ctx
}