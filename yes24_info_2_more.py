from bs4 import BeautifulSoup as bs
import requests

# 검색할 키워드 입력
query = input('키워드를 입력하세요: ')

# 검색 결과를 담을 리스트 초기화
data_list = []

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
        
        print(f"제목: {title} \n링크: https://www.yes24.com{href} \n출판사: {pub}")
        print(f"저역자: {auth} \n출간일: {date} \n정가: {price} \n판매지수: {sales} \n쪽수, 무게, 크기: {page}")
