#!/usr/bin/env bash
set -euo pipefail

touch pyproject.toml
mkdir -p src/testbench
mkdir -p src/testbench/shared

# Infrastructure
mkdir -p src/testbench/persistence
mkdir -p src/testbench/api/routers
mkdir -p src/testbench/web/static/css
mkdir -p src/testbench/web/static/js
mkdir -p src/testbench/web/templates/layouts
mkdir -p src/testbench/web/templates/pages
mkdir -p src/testbench/web/templates/components

# Core bounded contexts (domain + application layers)
mkdir -p src/testbench/projects/domain/events
mkdir -p src/testbench/projects/application
mkdir -p src/testbench/campaigns/domain/events
mkdir -p src/testbench/campaigns/application
mkdir -p src/testbench/execution/domain/events
mkdir -p src/testbench/execution/application
mkdir -p src/testbench/dut_monitoring/domain/events
mkdir -p src/testbench/dut_monitoring/application

# Supporting bounded contexts
mkdir -p src/testbench/instruments/drivers

# Subsystem placeholders (implemented later)
mkdir -p src/testbench/subsystems/rcu/domain
mkdir -p src/testbench/subsystems/rcu/tests
mkdir -p src/testbench/subsystems/eps/domain
mkdir -p src/testbench/subsystems/eps/tests
mkdir -p src/testbench/subsystems/payload_5g/domain
mkdir -p src/testbench/subsystems/payload_5g/tests
mkdir -p src/testbench/subsystems/obc/domain
mkdir -p src/testbench/subsystems/obc/tests
mkdir -p src/testbench/subsystems/comms_ttc/domain
mkdir -p src/testbench/subsystems/comms_ttc/tests
mkdir -p src/testbench/subsystems/adcs/domain
mkdir -p src/testbench/subsystems/adcs/tests

# Create empty __init__.py in every Python package
find src/testbench -type d \
  ! -path '*/static*' ! -path '*/templates*' \
  -exec touch {}/__init__.py \;


