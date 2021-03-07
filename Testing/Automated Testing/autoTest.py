import requests, json, sys
from colorama import init, Fore, Style

configVars = {}


def main():
    init(convert=True) # Initialise colorama
    passedTests = 0
    failedTests = 0
    try:
        configPath = sys.argv[1]
    except Exception as e:
        print("Invalid parameters. Usage: py autoTest.py configPath")
        sys.exit(1)
    print(f"Reading config at {configPath}...")
    config = readConfig(configPath)
    
    for name, value in config["config"].items():
        configVars[name] = value
    print("Read config.")

    print("Beginning tests:")
    for test in config["tests"]:
        result = performTest(test)
        if result == True: # Successful test
            passedTests += 1
        else: # Failed test
            failedTests += 1
    totalTests = passedTests+failedTests
    successRate = passedTests/totalTests
    print("======================================")
    print("Final results:")
    print(f"Total tests: {totalTests}")
    print(f"Successful tests: {Fore.GREEN}{passedTests}{Style.RESET_ALL}")
    print(f"Failed tests: {Fore.RED}{failedTests}{Style.RESET_ALL}")
    if successRate < 0.5:
        print(f"Success rate: {Fore.RED}{round(successRate*100, 2)}%{Style.RESET_ALL}")
    elif successRate >= 0.5 and successRate <= 0.8:
        print(f"Success rate: {Fore.YELLOW}{round(successRate*100, 2)}%{Style.RESET_ALL}")
    else:
        print(f"Success rate: {Fore.GREEN}{round(successRate*100, 2)}%{Style.RESET_ALL}")

def performTest(testData):
    # Required parameters
    try:
        url = configVars[testData["url"]] + testData["path"]
        params = testData["params"]
        method = testData["method"]
        body = testData["body"]
        expectedResponseCodes = testData["expectedResponseCodes"]
    except Exception as e:
        recordInvalidTest(testData, f"Missing parameter {e}")
        return False
    try:
        if method == "get":
            r = requests.get(url, params=params, data=body)
        elif method == "post":
            r = requests.post(url, params=params, data=body)
        elif method == "put":
            r = requests.put(url, params=params, data=body)   
        else:
            recordInvalidTest(testData, f"Method {method} not supported.")
            return False
    except Exception as e: # Handle cases where there is no response from server
        recordFailedTest(testData, "", e)
        return
    statusCode = r.status_code
    if str(statusCode) in expectedResponseCodes:
        recordSuccessfulTest(testData, statusCode, r.json())
        return True
    else:
        recordFailedTest(testData, statusCode, r.json())
        return False

def recordFailedTest(testData, statusCode, response):
    print("======================================")
    print(f"{Fore.RED}FAILED{Style.RESET_ALL}")
    print(f"Test {Fore.GREEN}\"{testData['name']}\"{Style.RESET_ALL}")
    print(f"Method: {Fore.BLUE}{testData['method'].upper()}{Style.RESET_ALL}")
    print(f"Expected response codes: {testData['expectedResponseCodes']}")
    print(f"Received reponse code: {Fore.YELLOW}{statusCode}{Style.RESET_ALL}")
    print(f"Reponse: {response}")

def recordSuccessfulTest(testData, statusCode, response):
    print("======================================")
    print(f"{Fore.GREEN}PASSED{Style.RESET_ALL}")
    print(f"Test {Fore.GREEN}\"{testData['name']}\"{Style.RESET_ALL}")
    print(f"Method: {Fore.BLUE}{testData['method'].upper()}{Style.RESET_ALL}")
    print(f"Expected response codes: {testData['expectedResponseCodes']}")
    print(f"Received reponse code: {Fore.GREEN}{statusCode}{Style.RESET_ALL}")
    if len(str(response)) > 500:
        response = str(response)[:500]+f"{Fore.GREEN}(truncated){Style.RESET_ALL}"
    print(f"Reponse: {response}")

# For tests that were incorrectly specified:
def recordInvalidTest(testData, reason):
    print("======================================")
    print(f"{Fore.RED}FAILED{Style.RESET_ALL}")
    print(f"Test {Fore.GREEN}\"{testData['name']}\"{Style.RESET_ALL}")
    print(f"Method: {Fore.BLUE}{testData['method'].upper()}{Style.RESET_ALL}")
    print(f"Test config error. {reason}")

def readConfig(configPath):
    f = open(configPath, "r")
    contents = f.read()
    f.close()
    jsonContents = json.loads(contents)
    return jsonContents

if __name__ == "__main__":
    main()