import re
import requests
import os
from tqdm.auto import tqdm
from threading import Thread
from itertools import islice

def chunk(arr_range, arr_size):
    arr_range = iter(arr_range)
    return iter(lambda: tuple(islice(arr_range, arr_size)), ())

def write_txt(path, content):
    with open(path, 'w', encoding="utf8") as f:
        for line in content:
            f.write(f"{line}\n")
    f.close()

def open_txt(path):
    with open(path, 'r', encoding="utf8") as f:
        content = [word.split("\n")[0] for word in f]
    f.close()
    return content
    
def download_file(url, folder_path, file_name = None):
    response = requests.get(url, stream=True)
    if file_name is None:
        file_name = os.path.join(folder_path, os.path.basename(url))
    else:
        file_name = os.path.join(folder_path, file_name+'.png')
    
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    return file_name


def create_dataset_structure(base_folder):
    images_folder = os.path.join(base_folder, 'images')
    videos_folder = os.path.join(base_folder, 'videos')

    # Tạo thư mục dataset và các thư mục con
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(videos_folder, exist_ok=True)

    return images_folder, videos_folder



def shopee_crawl_from_url(url, down_load = True):
    r = re.search(r"i\.(\d+)\.(\d+)", url)
    shop_id, item_id = r[1], r[2]
    ratings_url = "https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={offset}&shopid={shop_id}&type=0"

    offset = 0
    datasets = []
    base_folder = os.path.join('shopee_crawl', item_id)
    images_folder, videos_folder = create_dataset_structure(base_folder)

    while True:
        data = requests.get(
            ratings_url.format(shop_id=shop_id, item_id=item_id, offset=offset)
        ).json()
        i = 1
        
        
        for i, rating in tqdm(enumerate(data["data"]["ratings"], 1)):
            d = rating["author_username"] + "|" + str(rating["rating_star"]) + "|" + rating["comment"]
            images_name = rating["images"]
            images_urls = ['https://down-bs-vn.img.susercontent.com/'+x+'_tn.webp&quot' for x in images_name]

            videos_urls= rating["videos"]
            videos_urls = [x['url'] for x in videos_urls]

            for image_url,name in zip(images_urls, images_name):
                
                download_file(image_url, images_folder, name)

            for video_url in videos_urls:
                download_file(video_url, videos_folder)

            datasets.append(d)
        if i % 20:
            break

        offset += 20
    
    write_txt(path=base_folder + "/comment.txt")
    print('Finished Crawler')
    return item_id, datasets

path_url = input("Nhập đường dẫn txt chứa các url sản phẩm: ")
path_url = path_url.strip()
urls = open_txt(path=path_url)

number_threads = int(input("Nhập số luồng: "))

sessions = list(chunk(arr_range=range(len(urls)),
                arr_size=number_threads))

for index_session in range(len(sessions)):
    threads = []
    for i in sessions[index_session]:
        print("Đang crawl từ url: ", urls[i])
        threads.append(Thread(target=shopee_crawl_from_url, args=(urls[i],)))
        
    for thread in threads:
        if not thread.is_alive():
            thread.start()
    for thread in threads:
        thread.join()
        

