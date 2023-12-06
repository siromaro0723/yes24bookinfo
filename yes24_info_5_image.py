import os
import pandas as pd
import re 
from bs4 import BeautifulSoup as bs
import requests
import urllib.request
import time

# 실행 파일이 아닌 경우에만 입력을 받음
if __name__ == "__main__":
    # 메시지 출력
    print('Yes24의 1~3페이지 검색 결과가 출력됩니다. \n키워드를 입력하세요:')

    # 검색할 키워드 입력
    query = input('')

# 검색 결과를 담을 리스트 초기화
data_list = []

# 이미지를 저장할 폴더 생성
image_folder = "book_covers"
os.makedirs(image_folder, exist_ok=True)

# 여러 페이지에 걸쳐 정보 수집
for page in range(1, 4):  # 여기서 1부터 3페이지까지
    # 각 페이지의 URL 설정
    url = f'https://www.yes24.com/Product/Search?domain=ALL&query={query}&Page={page}&order=SINDEX_ONLY'

    # requests 패키지를 이용해 'url'의 html 문서 가져오기
    response = requests.get(url)
    html_text = response.text

    # beautifulsoup 패키지로 파싱 후, 'soup' 변수에 저장
    soup = bs(response.text, 'html.parser')

    # CSS 선택자를 사용하여 도서 정보 추출
    book_info = soup.select("div.item_info")

    # 각 페이지에서 도서 정보만 추출
    for info in book_info[:24]:
        # [eBook], '[중고도서]'가 포함된 도서는 제외
        if '[eBook]' in info.get_text() or '[중고도서]' in info.get_text():
            continue

        # 도서 정보 페이지에 접근하기
        book_page_url = f"https://www.yes24.com{info.select_one('a.gd_name')['href']}"
        book_page_response = requests.get(book_page_url)
        book_page_soup = bs(book_page_response.text, 'html.parser')

        # 도서 제목 및 링크 정보 가져오기
        title_tag = book_page_soup.select_one("h2.gd_name")
        title = title_tag.get_text() if title_tag else "정보 없음"
        href = f"https://www.yes24.com{info.select_one('a.gd_name')['href']}"

        # 출판사 정보 가져오기
        pub_tag = book_page_soup.select_one("span.gd_pub")
        pub = pub_tag.get_text() if pub_tag else "정보 없음"

        # 저역자 정보 가져오기
        auth_tag = book_page_soup.select_one("span.gd_auth")
        auth = auth_tag.get_text().split('|')[0].strip().replace('정보 더 보기/감추기', '') if auth_tag else "정보 없음"

        # 출간일 정보 가져오기
        date_tag = book_page_soup.select_one("tbody > tr:nth-child(1) > td.txt.lastCol")
        date = date_tag.get_text() if date_tag else "정보 없음"

        # 도서 판매지수 정보 가져오기
        sales_tag = info.select_one("span.saleNum")
        sales = sales_tag.get_text().split('|')[0].strip().replace('판매지수 ', '') if sales_tag else "정보 없음"

        # 도서 정가 가져오기
        price_tag = book_page_soup.select_one("span > em.yes_m")
        price = price_tag.get_text() if price_tag else "정보 없음"

        # 도서 품목 정보 가져오기
        page_tag = book_page_soup.select_one("tbody > tr:nth-child(2) > td.txt.lastCol")
        page = page_tag.get_text() if page_tag else "정보 없음"

        # 도서 표지 이미지 가져오기
        cover_tag = book_page_soup.select_one("span.gd_img > em.imgBdr > img[src^='https://image.yes24.com/goods/']")
        cover_url = cover_tag['src'] if cover_tag else None

        # 이미지를 저장할 파일 경로 생성
        image_path = None
        if cover_url:
            # 도서 제목에서 특수문자 제거
            title_for_filename = re.sub(r'[\\/:*?"<>|]', '_', title)[:50]  # 파일명 제한 길이 50자로 설정
            image_filename = f"{title_for_filename}.jpg"
            image_path = os.path.join(image_folder, image_filename)

            # 표지 다운로드
            urllib.request.urlretrieve(cover_url, image_path)

            # 이미지 저장이 완료될 때까지 대기
            while not os.path.exists(image_path):
                time.sleep(1)

        # 데이터 추가
        data_list.append({
            '제목': title,
            '링크': href,
            '출판사': pub,
            '저역자': auth,
            '출간일': date,
            '정가': price,
            '판매지수': sales,
            '쪽수, 무게, 크기': page,
        })

# 데이터프레임 생성
df = pd.DataFrame(data_list)

# csv 파일로 저장
csv_file_path = "yes24bookinfo.csv"
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

print(f"도서 정보 {csv_file_path} 파일과 표지가 저장되었습니다.")