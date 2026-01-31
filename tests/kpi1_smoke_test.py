import pytest
from bs4 import BeautifulSoup

from src import kpi1_extract


@pytest.fixture
def sample_soup():
    html = """
    <html>
      <head><title>TE37 Sonic Wheels</title></head>
      <body>
        <h1>RAYS TE37 Sonic 15インチ</h1>
        <div class="ProductPrice">120000</div>
        <div id="ProductPhoto">
          <img src="https://example.com/image1.jpg" />
          <img src="https://example.com/image2.jpg" />
        </div>
        <div id="ProductDescription">
          <p>メーカー：RAYS モデル：TE37 リム幅7J PCD100 OFFSET+35</p>
        </div>
        <div class="ProductDetail__shipping">送料込み</div>
      </body>
    </html>
    """
    return BeautifulSoup(html, "lxml")


def test_extract_listing(monkeypatch, sample_soup):
    monkeypatch.setattr("src.kpi1_extract.fetch_html", lambda url: sample_soup)
    result = kpi1_extract.extract_listing("https://auctions.yahoo.co.jp/sample")

    assert result["title"] == "RAYS TE37 Sonic 15インチ"
    assert result["price"] == "120000"
    assert result["shipping"] == "送料込み"
    assert result["photos"] == [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
    ]
    assert "メーカー" in result["description_html"]
