#!/bin/bash
if [ -z "$1" ]; then echo "Usage: $0 <version>"; exit 1; fi
echo "Rollback to $1..."
