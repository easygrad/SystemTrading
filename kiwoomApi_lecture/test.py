print("hello")

# vscode에서 파이썬 실행 시 "& was unexpected at this time." / "&은(는) 예상되지 않았습니다." 오류 발생

# 원인: vscode의 버전 문제
# 해결: Settings > 'terminal.integrated.default' 검색 후 'Edit in settings. json' 클릭 > 코드입력 ' "terminal.integrated.shell.windows": "C:\\Windows\\System32\\cmd.exe", ' 중간에 입력해줘야 하는데, 어디냐면,, 
#     "terminal.integrated.tabs.enabled": true,
#     "terminal.integrated.defaultProfile.windows": "Command Prompt",
#     "terminal.integrated.shell.windows": "C:\\Windows\\System32\\cmd.exe", #<< 여기!!
#     "terminal.integrated.profiles.windows": {

# 저장 후

# 터미널 다 죽이고 > 파이썬 파일 우클릭 > Open in integrated Terminal > 실행!