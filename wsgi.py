#!/usr/bin/env python
from flask import Flask
from wapp import app


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080, debug=True)
# end if

