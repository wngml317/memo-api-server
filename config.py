class Config :
    # 서명에 사용되는 Key 이고 직접 String으로 정의
    JWT_SECRET_KEY = 'yhacademy0317##hello'
    # Access 토큰의 만료 시간
    JWT_ACCESS_TOKEN_EXPIRES = False
    # 명시적으로 예외를 전파하는 것에 대한 활성화함(True)
    PROPAGATE_EXCEPTIONS = True