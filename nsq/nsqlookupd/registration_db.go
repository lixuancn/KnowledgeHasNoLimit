package nsqlookupd

import "sync"

type RegistrationDB struct{
	sync.WaitGroup
	registrationMap map[Registration]Producers
}

type Registration struct{
	Category string
	Key string
	SubKey string
}

type Registrations []Registration