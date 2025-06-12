import requests
import time
import threading

def download_data(url, result_container):
    result_container['response'] = requests.get(url)

def refresh_data():
    api_url = "https://data.eindhoven.nl/api/explore/v2.1/catalog/datasets/data-openbare-verlichting/exports/xlsx"
    print(f"Refreshing data from {api_url}...")

    start_time = time.time()
    print("Request started at:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)))

    result_container = {}

    download_thread = threading.Thread(target=download_data, args=(api_url, result_container))
    download_thread.start()

    while download_thread.is_alive():
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "- in progress...")
        time.sleep(1)

    download_thread.join()
    response = result_container.get('response')

    if response and response.status_code == 200:
        file_path = 'new_data_quality_kleurtemperatuur.xlsx'
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Data refreshed and saved to {file_path}")
    else:
        print(f"Failed to refresh data. Status code: {response.status_code if response else 'No response'}")

if __name__ == "__main__":
    refresh_data()
