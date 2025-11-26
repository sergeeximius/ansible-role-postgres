import os

# Use Molecule managed hosts - testinfra will discover all hosts from inventory
testinfra_hosts = [
    f"ansible://all?ansible_inventory={os.environ['MOLECULE_INVENTORY_FILE']}"
]


def test_postgresql_service_running(host):
    """Test that PostgreSQL service is running and enabled."""
    postgresql = host.service("postgresql")
    assert postgresql.is_running, "PostgreSQL service is not running"
    assert postgresql.is_enabled, "PostgreSQL service is not enabled"


def test_postgresql_socket_exists(host):
    """Test that PostgreSQL socket exists."""
    # Check for Unix socket in /var/run/postgresql
    socket_dir = host.file("/var/run/postgresql")
    assert socket_dir.exists, "/var/run/postgresql does not exist"
    assert socket_dir.is_directory, "/var/run/postgresql is not a directory"


def test_postgresql_listening(host):
    """Test that PostgreSQL is listening on port 5432."""
    socket = host.socket("tcp://127.0.0.1:5432")
    assert socket.is_listening, "PostgreSQL is not listening on port 5432"


def test_postgresql_user_exists(host):
    """Test that postgres user exists."""
    user = host.user("postgres")
    assert user.exists, "postgres user does not exist"


def test_postgresql_config_exists(host):
    """Test that PostgreSQL main config exists."""
    # Ubuntu 24.04 uses PostgreSQL 16
    possible_paths = [
        "/etc/postgresql/16/main/postgresql.conf",
        "/etc/postgresql/15/main/postgresql.conf",
        "/etc/postgresql/14/main/postgresql.conf",
    ]

    exists = False
    for path in possible_paths:
        if host.file(path).exists:
            exists = True
            break

    assert exists, f"PostgreSQL config not found in any of: {possible_paths}"


def test_pg_hba_config_exists(host):
    """Test that pg_hba.conf exists."""
    possible_paths = [
        "/etc/postgresql/16/main/pg_hba.conf",
        "/etc/postgresql/15/main/pg_hba.conf",
        "/etc/postgresql/14/main/pg_hba.conf",
    ]

    exists = False
    for path in possible_paths:
        if host.file(path).exists:
            exists = True
            break

    assert exists, f"pg_hba.conf not found in any of: {possible_paths}"


def test_test_database_exists(host):
    """Test that test database was created."""
    cmd = host.run(
        "sudo -u postgres psql -tAc \"SELECT 1 FROM pg_database WHERE datname='test'\""
    )
    assert cmd.stdout.strip() == "1", "Test database does not exist"


def test_test_user_exists(host):
    """Test that test user was created."""
    cmd = host.run(
        "sudo -u postgres psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='test'\""
    )
    assert cmd.stdout.strip() == "1", "Test user does not exist"
