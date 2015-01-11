SimpleOnCall
============

Open source ops on-call scheduling application.


## Project Progress

The project's progress can be tracked with github issues or with the project's
[waffle board](https://waffle.io/simpleoncall/simpleoncall).

[![Stories in Ready](https://badge.waffle.io/simpleoncall/simpleoncall.svg?label=ready&title=Ready)](http://waffle.io/simpleoncall/simpleoncall)
[![Stories in Progress](https://badge.waffle.io/simpleoncall/simpleoncall.svg?label=in%20progress&title=In%20Progress)](http://waffle.io/simpleoncall/simpleoncall)

## Development Setup

The following are the necessary commands needed to get started running a
development version of SimpleOnCall, using the default sqlite db backend for
Django.

`pip` and `npm` will both be required.

```bash
git clone git://github.com/simpleoncall/simpleoncall.git
cd ./simpleoncall
# this will install all python and node.js requirements
make deps
# this will run migrations and start the development django server
make runserver
```
