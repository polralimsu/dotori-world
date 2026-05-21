# 도토리 월드 (DOTORi World) 🐿️

Django로 구축된 레트로 감성의 소셜 네트워크 플랫폼 ("미니홈피") 입니다.

## 🌟 주요 기능
- **사용자 인증**: 회원가입, 로그인, 프로필 관리.
- **이메일 기반 보안 (추가)**: 회원가입 시 이메일 인증 필수 활성화, 이메일을 통한 아이디 찾기 및 비밀번호 재설정 기능 제공 (SMTP 및 AWS SES 연동 지원).
- **미니홈피**: 메인 동영상과 상태 메시지로 나만의 프로필을 꾸밀 수 있습니다.
- **게시판 및 댓글**: 사진과 글을 공유하고 댓글로 소통할 수 있습니다.
- **일촌 (친구)**: 일촌 신청을 주고받고, "일촌평"을 남길 수 있습니다.
- **음악 상점 (도토리)**: 가상 화폐(도토리)를 충전하여 내 미니홈피의 BGM을 구매할 수 있습니다.
- **파도타기 (랜덤 이동)**: 다른 사용자의 미니홈피를 무작위로 방문합니다.
- **다국어 지원**: 전체 UI 언어 변경(한국어/영어/일본어) 및 게시글, 일촌평에 대한 실시간 번역(Amazon Translate 연동)을 지원합니다.
- **AWS 연동**: Amazon S3를 통한 미디어 및 정적 파일 클라우드 저장, Amazon Translate를 통한 동적 텍스트 번역을 지원합니다.

## 📋 필수 요구 사항
- **Python 3.12** 이상 (Django 6.0 구동 기준)
- MySQL / MariaDB (운영 환경) 또는 SQLite (개발/테스트용)
- AWS 계정 (S3 버킷, AWS Translate 및 AWS SES 접근 권한 필요)

---

## 🚀 배포 가이드

### 1. 클론 및 의존성 설치
```bash
git clone <repository_url>
cd pythonWeb
python3.12 -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)
환경 변수 예시 파일을 복사한 후 운영 서버에 맞게 정보를 설정하세요. 실제 운영 환경에서는 반드시 `DEBUG=False`로 설정해야 합니다.
```bash
cp .env.example .env
```
- `DATABASE_URL`이 실제 데이터베이스를 가리키도록 설정합니다. (입력하지 않거나 주석 처리 시 SQLite가 자동 사용됩니다.)
- 이메일 인증 기능 사용을 위해 이메일 호스트(SMTP) 또는 AWS SES 설정을 완료하세요.
- **AWS ALB(로드밸런서) 경유 시**: CSRF 보안 검증 통과를 위해 `.env` 파일에 실제 접속할 도메인을 반드시 입력해야 합니다.
  ```ini
  CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
  ```

### 3. 데이터베이스 마이그레이션 (DB 초기화)
```bash
python manage.py migrate
```

### 4. 번역 파일 컴파일
다국어 지원을 위한 언어 메시지 파일을 컴파일합니다:
```bash
python create_translations.py
```

### 5. 정적 파일 수집 (Static Files)
운영 환경에서 서비스하기 위해 모든 정적 파일(CSS, JS 등)을 수집합니다. S3 연동이 설정된 경우 S3 버킷으로 자동 업로드됩니다:
```bash
python manage.py collectstatic --noinput
```

### 6. 운영 서버 실행 방법

**Linux (Gunicorn):**
```bash
pip install gunicorn
# 80번 포트 바인딩 시 관리자 권한(sudo)이 필요할 수 있습니다.
gunicorn config.wsgi:application --bind 0.0.0.0:80 --workers 3
```

**Windows (Waitress):**
```bash
pip install waitress
waitress-serve --port=80 config.wsgi:application
```

---

## 🛠️ AWS 배포 및 연동 핵심 설정

### 1. S3 및 CloudFront 스토리지 분리 관리 (Static & Media)
정적 파일(static)과 유저 업로드 미디어(media)는 S3 버킷 내의 독립된 디렉토리에 나누어 저장됩니다.
- **`/static/`**: CSS, JS, 이미지 에셋
- **`/media/`**: 사용자 프로필 이미지, 동영상, BGM 음악 파일

**💡 보안 권장사항:**
- 만약 CloudFront의 **OAC(Origin Access Control)** 설정을 이용해 S3 버킷을 연결하는 경우, S3 버킷 자체의 퍼블릭 차단을 풀거나 `"Principal": "*"` 정책을 적용할 필요가 없습니다. 
- 버킷 정책에 **CloudFront 배포 ID에 대해서만 `s3:GetObject` 권한을 허용**하여 다이렉트 S3 접근을 방지하는 것이 최선의 보안 규칙입니다.
