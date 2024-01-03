## v1.12.0

2024-01-13

-   only allow one registration for now: the first admin user until there's a need for more public-facing registrations (additional users can be created via user create endpoint)
-   add app configured default per_page and max_per_page
-   add status to access node updates, make all parameters optional
-   clear device node and user assignments on device archive
-   add filtering device list by user id
-   set assigned access cards to inactive when user updated to not active
-   unassign cards when archiving user
-   update access node statuses to fit with nodes in use now

## v1.11.0

2023-12-01

-   enable database migrations with flask-migrate

## v1.10.0

2023-11-28

-   add reporting endpoints

## v1.9.0

2023-11-25

-   fill in additional profile data for users, access nodes, devices
-   add an access node "scan" endpoint for access node manual overrides and testing

## v1.8.0

2023-11-24

-   add device user assignments and assignment logging

## v1.7.0

2023-11-23

-   add access card user assignments

## v1.6.0

2023-11-16

-   add user endpoints

## v1.5.0

2023-11-16

-   local secrets file
-   support secrets in GitHub actions

## v1.4.0

2023-11-09

-   set device status with create and edit

## v1.3.0

2023-11-09

-   revise data model to accommodate access card system requirements
-   add access card endpoints

## v1.2.0

2023-11-09

-   add access node endpoints

## v1.1.0

2023-11-09

-   archive devices not delete
-   placeholder device log endpoint
-   models formatting, cleanup

## v1.0.1

2023-11-09

-   created github actions

## v.1.0.0

2023-11-09

-   initial project setup
