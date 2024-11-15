import logging
from main import run_monitor_instance

# Mock configuration for testing
mock_config = {
    "entry_site": {
        "url": "https://speedd8.se/event-goteborg/",
        "selectors": {
            "entry": "div.e-con-inner",
            "title": "h3.elementor-heading-title a",
            "place": "a[itemprop='url'] span[itemprop='name']",
            "time_age": "div.elementor-widget-theme-post-excerpt"
        }
    },
    "check_interval": 86400,
    "filters": {
        "filter_type": "positive",
        "title_filter": ["Projektledare"],
        "location_filter": ["Stockholm", "Uppsala", "Göteborg"],
        "age_filter": "30"
    },
    "debug": {
        "stop_after_one": True
    },
    "send_starting_entries": True
}

def test_run_monitor_instance():
    try:
        # Run the function with the mock configuration
        run_monitor_instance(mock_config)
        print("run_monitor_instance executed successfully.")
    except Exception as e:
        logging.error(f"Error during test: {e}")
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_run_monitor_instance() 