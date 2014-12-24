SimpleOnCall
============

Open source ops on-call scheduling application.


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
