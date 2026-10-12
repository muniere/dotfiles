package platform

import "runtime"

type Platform string

const (
	Linux   Platform = "linux"
	Darwin  Platform = "darwin"
	Default Platform = "default"
)

func Identify() Platform {
	switch runtime.GOOS {
	case "linux":
		return Linux
	case "darwin":
		return Darwin
	default:
		return Default
	}
}
