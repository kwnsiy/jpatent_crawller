# coding: utf-8

"""
特許の審査経過情報を自動取得
"""

import pdb
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pprint import pprint 
from selenium.webdriver.chrome.options import Options

class Crawller():

  def __init__(self, sleep_time, headless=False):
    self.sleep_time   = sleep_time
    self.headless     = headless
    options = Options()
    if self.headless:
      options.add_argument("--headless")  

    self.driver       = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    self.driver.get("https://www.j-platpat.inpit.go.jp/s0100")
    self.search_window = self.driver.window_handles[0]
    self.progress_window         = None 
    self.report_window_          = None 
    time.sleep(self.sleep_time)
  
  # ページの最後までスクロール
  def scroll_all(self):
    pre_html = None
    while not self.driver.page_source == pre_html:
        pre_html = self.driver.page_source
        self.driver.execute_script("window.scrollBy(0, 7000);")
        time.sleep(self.sleep_time*0.5)

  # 検索結果の一覧を取得
  def get_search_candidates(self, query):
    results = []
    self.driver.switch_to.window(self.search_window) # 常に0番目は検索画面
    self.driver.find_element(By.ID, "s01_srchCondtn_txtSimpleSearch").send_keys(query)
    self.driver.find_element(By.ID, "s01_srchBtn_btnSearch").click()
    time.sleep(self.sleep_time)
    self.scroll_all()
    tbody_element = self.driver.find_element(By.TAG_NAME, "tbody")
    tr_elements   = tbody_element.find_elements(By.TAG_NAME, "tr")
    for i, i_tr in enumerate(tr_elements):
      # ヒットした特許番号と経過情報リンクのペア
      if len(i_tr.find_elements(By.ID, "patentUtltyIntnlSimpleBibLst_tableView_progReferenceInfo%s" % str(i))): 
        results.append([i_tr.text.split("\n")[1], i_tr.find_element(By.ID, "patentUtltyIntnlSimpleBibLst_tableView_progReferenceInfo%s" % str(i))])
      else: 
        results.append([i_tr.text.split("\n")[1], i_tr.find_element(By.ID, "patentUtltyIntnlNumOnlyLst_tableView_progReferenceInfo%s" % str(i))]) 
    return results
  
  # 経過情報ページに遷移
  def move_progress_information(self, target_application): 
    self.driver.switch_to.window(self.search_window)
    target_application.click()
    self.progress_window = self.driver.window_handles[-1]
    self.driver.switch_to.window(self.progress_window)
    time.sleep(self.sleep_time)


  # 経過情報の一括取得
  def get_reports(self, query, target_reports=["明細書", "請求の範囲", "要約書", "特許検索報告書", "拒絶理由通知書"]): # 明細書, 請求の範囲, 要約書, 特許検索報告書, 拒絶理由通知書
    outputs  = [] 
    results = self.get_search_candidates(query)
    print ("query:", query, "hits:", len(results))
    if results:
      for result in results:
        print ("---")
        print (result[0])
        self.move_progress_information(result[1])
        output      = {"検索クエリ": query, "文献番号": result[0]}
        for target_report in target_reports:
            print (target_report)
            self.driver.switch_to.window(self.progress_window)
            report_link = self.driver.find_elements(By.XPATH, "//a[contains(text(), '%s')]" % target_report)
            if len(report_link) > 0: 
              print ("Available")
              report_link[0].click()
              time.sleep(self.sleep_time)
              self.report_window_ = self.driver.window_handles[-1]
              self.driver.switch_to.window(self.report_window_)
              html_content = self.driver.page_source
              soup = BeautifulSoup(html_content, "html.parser")
              text = soup.find_all("pre")
              output["target_report"] = text
              self.driver.close()
            else: 
              print ("None")
        outputs.append(output)
        self.driver.switch_to.window(self.progress_window)
        self.driver.close()
    return outputs


  # 一件のみ取得
  def get_report(self, query, target_reports=["明細書", "請求の範囲", "要約書", "特許検索報告書", "拒絶理由通知書"]): # 明細書, 請求の範囲, 要約書, 特許検索報告書, 拒絶理由通知書
    outputs  = [] 
    results = self.get_search_candidates(query)
    print ("query:", query, "hits:", len(results))
    if results:
      print ("---")
      print (results[0][0])
      self.move_progress_information(results[0][1])
      output      = {"検索クエリ": query, "文献番号": results[0][0]}
      for target_report in target_reports:
          print (target_report)
          self.driver.switch_to.window(self.progress_window)
          report_link = self.driver.find_elements(By.XPATH, "//a[contains(text(), '%s')]" % target_report)
          if len(report_link) > 0: 
            print ("Available")
            report_link[0].click()
            time.sleep(self.sleep_time)
            self.report_window_ = self.driver.window_handles[-1]
            self.driver.switch_to.window(self.report_window_)
            html_content = self.driver.page_source
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.find_all("pre")
            output["target_report"] = text
            self.driver.close()
          else: 
            print ("None")
      outputs.append(output)
      self.driver.switch_to.window(self.progress_window)
      self.driver.close()
    return outputs

if __name__ == "__main__":
    
    crawller        = Crawller(6)
    pprint(crawller.get_reports("農業 人工知能 センサー"))
    
    crawller        = Crawller(6,  headless=True)
    pprint(crawller.get_reports("農業 人工知能 センサー"))

    crawller        = Crawller(6,  headless=True)
    pprint(crawller.get_report("特願2020-086759"))

    crawller        = Crawller(8,  headless=True)
    pprint(crawller.get_report("特願2020-086759", target_reports=["特許検索報告書"]))
    
