import os

def global_settings(request):
    # 모든 템플릿에서 사용할 전역 변수를 딕셔너리 형태로 정의합니다.
    return {
        'TOSS_CLIENT_KEY': os.environ.get('TOSS_CLIENT_KEY')
    }