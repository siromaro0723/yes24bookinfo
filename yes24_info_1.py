# 프로젝트에 필요한 패키지 불러오기
from bs4 import BeautifulSoup as bs
import requests

# 검색할 키워드 입력
query = input('키워드를 입력하세요: ')

# step3.입력받은 query가 포함된 url 주소(Yes24 검색 결과 페이지) 저장
url = 'https://www.yes24.com/Product/Search?domain=ALL&query='+'%s'%query

# requests 패키지를 이용해 'url'의 html 문서 가져오기
response = requests.get(url)
html_text = response.text

# beautifulsoup 패키지로 파싱 후, 'soup' 변수에 저장
soup = bs(response.text, 'html.parser')

# CSS 선택자를 사용하여 도서 정보 추출
book_info = soup.select("div.item_info")

# 각 도서 정보 출력
for info in book_info[:23]:
    title = info.select_one("a.gd_name").get_text()
    href = info.select_one("a.gd_name").attrs['href']
    pub = info.select_one("span.authPub.info_pub").get_text()
    auth = info.select_one("span.authPub.info_auth").get_text().split('|')[0].strip().replace('정보 더 보기/감추기', '')
    date = info.select_one("span.authPub.info_date").get_text()
    price = soup.select_one("strong.txt_num").get_text()
    sales = soup.select_one("span.saleNum").get_text().split('|')[0].strip().replace('판매지수 ', '')

    print(f"제목: {title} \n링크: https://www.yes24.com{href} \n출판사: {pub}")
    print(f"저역자: {auth} \n출간일: {date} \n정가: {price} \n판매지수: {sales}")

