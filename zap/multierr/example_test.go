package multierr_test

import (
	"errors"
	"fmt"
	"zap/multierr"
)

func ExampleCombine() {
	err := multierr.Combine(
		errors.New("call 1 failed"),
		nil, // successful request
		errors.New("call 3 failed"),
		nil, // successful request
		errors.New("call 5 failed"),
	)
	fmt.Printf("%+v", err)
	// Output:
	// the following errors occurred:
	//  -  call 1 failed
	//  -  call 3 failed
	//  -  call 5 failed
}

func ExampleAppend() {
	var err error
	err = multierr.Append(err, errors.New("call 1 failed"))
	err = multierr.Append(err, errors.New("call 2 failed"))
	fmt.Println(err)
	// Output:
	//  -  call 1 failed
	//  -  call 2 failed
}

func ExampleErrors() {
	err := multierr.Combine(
		nil, // successful request
		errors.New("call 2 failed"),
		errors.New("call 3 failed"),
	)
	err = multierr.Append(err, nil) // successful request
	err = multierr.Append(err, errors.New("call 5 failed"))

	errors := multierr.Errors(err)
	for _, err := range errors {
		fmt.Println(err)
	}
	// Output:
	//  -  call 2 failed
	//  -  call 3 failed
	//  -  call 5 failed
}
