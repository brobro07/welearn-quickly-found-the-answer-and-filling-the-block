from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

opt = Options()
opt.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Edge(options=opt)

try:
    driver.switch_to.frame(0)
    wait = WebDriverWait(driver, 15)
    time.sleep(2)

    # ---------------------- 1. 处理【选词填空】自动选词 ----------------------
    word_inputs = driver.find_elements("css selector", "input[data-solution][data-index]")
    if word_inputs:
        print("🔍 开始处理【选词填空】...")
        # ✅ 修正词库定位器：匹配你页面真实的 ul 结构
        word_options = driver.find_elements("css selector", "ul.ChooseSheet_cell span")
        word_dict = {el.text.strip(): el for el in word_options}
        print("词库加载完成，共", len(word_dict), "个选项")
        print("词库内容：", list(word_dict.keys()))

        for i, input_el in enumerate(word_inputs):
            ans = input_el.get_attribute("data-solution")
            print(f"第 {i+1} 空答案：{ans}")

            # 用 JS 触发点击激活输入框
            driver.execute_script("arguments[0].click();", input_el)
            time.sleep(0.2)

            # 找到词库中对应的答案词并点击
            if ans in word_dict:
                word_el = word_dict[ans]
                driver.execute_script("arguments[0].click();", word_el)
                time.sleep(0.3)
                print(f"✅ 已点击选择：{ans}")
            else:
                print(f"❌ 词库中未找到答案：{ans}")
        print(f"✅ 【选词填空】已完成，共 {len(word_inputs)} 题")
    else:
        print("ℹ️  未检测到【选词填空】")

    # ---------------------- 2. 处理【填空题/主观题】 ----------------------
    input_elements = driver.find_elements("css selector", "input[data-solution]:not([data-index]), textarea[data-solution]")
    if input_elements:
        print("\n🔍 开始处理【填空题/主观题】...")
        for i, el in enumerate(input_elements):
            time.sleep(0.3)
            ans = el.get_attribute("data-solution")
            driver.execute_script("arguments[0].value = arguments[1];", el, ans)
            time.sleep(0.3)
        print(f"✅ 【填空题/主观题】已完成，共 {len(input_elements)} 题")
    else:
        print("ℹ️  未检测到【填空题/主观题】")

    # ---------------------- 3. 处理【选择题】 ----------------------
    choice_questions = driver.find_elements("css selector", "div[data-controltype='choice']")
    if choice_questions:
        print("\n🔍 开始处理【选择题】...")
        correct_options = driver.find_elements("css selector", "li[data-solution]")
        for opt in correct_options:
            wait.until(EC.element_to_be_clickable(opt))
            driver.execute_script("arguments[0].setAttribute('data-choiced', '')", opt)
            time.sleep(0.2)
        print(f"✅ 【选择题】已完成，共 {len(correct_options)} 题")
    else:
        print("ℹ️  未检测到【选择题】")

    print("\n🎉 所有题型处理完毕！")

finally:
    driver.switch_to.default_content()
