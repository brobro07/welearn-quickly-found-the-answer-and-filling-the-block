from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchFrameException, TimeoutException, NoSuchElementException
import time

opt = Options()
opt.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Edge(options=opt)
wait = WebDriverWait(driver, 15)

try:
    # 🔹 智能切换 frame：不存在则跳过，避免报错
    try:
        # 等待最多5秒，检查是否有 iframe 出现
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(0)
        print("✅ 已成功切换到 frame 0")
    except (NoSuchFrameException, TimeoutException) as e:
        print(f"⚠️  未检测到 frame，直接操作主页面：{str(e)}")

    time.sleep(2)

    # ---------------------- 1. 处理【选词填空】自动选词 ----------------------
    try:
        word_inputs = driver.find_elements("css selector", "input[data-solution][data-index]")
        if word_inputs:
            print("\n🔍 开始处理【选词填空】...")
            word_options = driver.find_elements("css selector", "ul.ChooseSheet_cell span")
            word_dict = {el.text.strip(): el for el in word_options}
            print(f"词库加载完成，共 {len(word_dict)} 个选项")

            for i, input_el in enumerate(word_inputs):
                ans = input_el.get_attribute("data-solution")
                print(f"第 {i+1} 空答案：{ans}")

                driver.execute_script("arguments[0].click();", input_el)
                time.sleep(0.2)

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
    except Exception as e:
        print(f"❌ 处理选词填空时出错：{str(e)}")

    # ---------------------- 2. 处理【填空题/主观题】 ----------------------
    try:
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
    except Exception as e:
        print(f"❌ 处理填空题时出错：{str(e)}")

    # ---------------------- 3. 处理【选择题】 ----------------------
    try:
        choice_questions = driver.find_elements("css selector", "div[data-controltype='choice']")
        if choice_questions:
            print("\n🔍 开始处理【选择题】...")
            correct_options = driver.find_elements("css selector", "li[data-solution]")
            for opt in correct_options:
                try:
                    wait.until(EC.element_to_be_clickable(opt))
                    driver.execute_script("arguments[0].setAttribute('data-choiced', '')", opt)
                    time.sleep(0.2)
                except Exception as e:
                    print(f"❌ 选择题选项点击失败：{str(e)}")
            print(f"✅ 【选择题】已完成，共 {len(correct_options)} 题")
        else:
            print("ℹ️  未检测到【选择题】")
    except Exception as e:
        print(f"❌ 处理选择题时出错：{str(e)}")

    print("\n🎉 所有题型处理完毕！")

finally:
    # 🔹 安全切回主 frame，避免残留
    try:
        driver.switch_to.default_content()
    except:
        pass
    # 🔹 如需关闭浏览器，取消下面注释
    # driver.quit()
