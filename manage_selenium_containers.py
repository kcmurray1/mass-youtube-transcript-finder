import docker
import time


def get_client(ip, user, port=22):
    # Otherwise, use the SSH tunnel logic we fixed earlier
    return docker.DockerClient(base_url=f"ssh://{user}@{ip}:{port}", use_ssh_client=True)

def teardown(hub_address, workers, test_node_user):
    for address in workers:
        try:
            client = get_client(address, test_node_user, 3595)
            containers = client.containers.list(all=True, filters={"name": "selenium-"})
            for c in containers:
                print(f"  Removing {c.name} from {address}...")
                c.remove(force=True)
        except Exception as e:
            print(f"  Could not reach {address}: {e}")

    # remove hub
    try:
        client = get_client(hub_address, "kman3431")
        containers = client.containers.list(all=True, filters={"name": "selenium-"})
        for c in containers:
            print(f"  Removing {c.name} from {hub_address}...")
            c.remove(force=True)
    except Exception as e:
        print(f"  Could not reach {address}: {e}")

def setup(hub_address, workers, test_node_user):
    teardown(hub_address, workers, test_node_user)
    print("\n🚀 Starting Selenium Hub...")
    hub_client = get_client(hub_address, "kman3431")
    
    hub_client.containers.run(
        "selenium/hub:4.39.0-20251212",
        detach=True,
        name="selenium-hub",
        ports={'4442/tcp': 4442, '4443/tcp': 4443, '4444/tcp': 4444},
        environment={
            "SE_EVENT_BUS_HOST": hub_address,
            "SE_EVENT_BUS_PUBLISH_PORT" : 4442,
            "SE_EVENT_BUS_SUBSCRIBE_PORT": 4443
        }
    )

    # Give the Hub a moment to initialize before nodes connect
    time.sleep(3)

    for i, node in enumerate(workers):
        client = get_client(node, test_node_user, 3595)
        
        client.containers.run(
            "selenium/node-chrome:4.39.0-20251212",
            name=f"selenium-node-{i}",
            shm_size="25g",
            ports={"5555/tcp":5555},
            detach=True,
            environment={
                "SE_EVENT_BUS_HOST":hub_address,
                "SE_NODE_HOST":node,
                "SE_NODE_PORT":5555,
                "SE_NODE_MAX_SESSIONS": 12,
                "SE_NODE_OVERRIDE_MAX_SESSIONS": "true"
            }
        )


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv

    load_dotenv()
    import os

    hub_address = os.getenv("HUB_HOST")
    test_node_address = os.getenv("TEST_NODE")
    test_node_user = os.getenv("TEST_NODE_USER")

    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        teardown(hub_address, test_node_address.split(','), test_node_user)
    else:
        setup(hub_address, test_node_address.split(','), test_node_user)