import requests


def download_state_dict(url, save_path):
    """
    Hugging Face state_dict 파일을 다운로드합니다.

    Args:
        url (str): 다운로드할 파일의 URL
        save_path (str): 저장할 파일 경로
    """
    print(f"Downloading state_dict from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"state_dict saved to {save_path}.")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


if __name__ == "__main__":
    # 다운로드 URL 및 저장 경로
    url = "https://huggingface.co/xxhyeok/koBERT-emotion/resolve/main/bert_classifier_model.pt"
    save_path = "koBERT-emotion/bert_classifier_model.pt"

    download_state_dict(url, save_path)