"""
Django settings for bookstore project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yfg@4mk0!17vaeujd3)m8#a3#rwj@4l#+4tah&5+9a%qu7fx(4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'user',
    'book',
    'order',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 模板搜索路径
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # 在INSTALLED_APPS中寻找templates子目录
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookstore.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# 时区
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# 会话设置
# 缓存并写到数据库
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
# 每次会话缓存
SESSION_SAVE_EVERY_REQUEST = True
# 默认：关闭浏览器后仍有效
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.qq.com'  # 如果是 163 改成 smtp.163.com
EMAIL_PORT = 465
EMAIL_HOST_USER = 'yusitong1999@qq.com'  # 帐号
EMAIL_HOST_PASSWORD = 'xcjzwgewebtpbccj'  # 密码
DEFAULT_FROM_EMAIL = 'yusitong <' + EMAIL_HOST_USER + '>'

# 使用本地时间
USE_TZ = False

# APP ID
ALIPAY_APPID = '2016102100732845'

# 网关
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'  # 沙箱网关，生产环境须更改为正式网关。

# 回调通知地址
ALIPAY_NOTIFY_URL = 'http://62.234.74.232:8000/order/pay_result/' # 如果生产环境或外网可以访问开发服务器
ALIPAY_RETURN_URL = ALIPAY_NOTIFY_URL

# 密钥字符串
APP_PRIVATE_KEY = 'MIIEpAIBAAKCAQEAjg25S81ssVM091Z1tvtZzCnLxWKR+mhaqAeRn7SjHeiV46AIt8kQnj0QK1IoZjHmUb0mDzisRlz6u83o+ftnOz2/1w6bvdPtgchYE0C6GXZHYc1W/uODzHjnFCMt/STb7/aHEh5GlIXidyIKz942tbRbgcq761mpw/pSnVUvLPbbR0WKvnEHXgMI0hnPdz8roXNFIp+E5DCbOAwp5Ff2VfLVV0zGYnVRhIWTec/yzbvnCArI6jvzG2r+CtRUqTAIkPyDok/X+nuvyck+TrI7b0rd4szzpatbfjrH2t6qq8yJV9sgV20Q6+uHRNwWD6Z+jlnEbyGuBuRFnAvyx7yw4wIDAQABAoIBACQGPvOGSQY/P7Np7bhVzdQE1XRdJwAF7tel87w4pxUyorBzKULSbrByc+NIlo40IWChQ0Gg8a92bO+rrGWY5/kSE9CKF9zwHc9H624WgBts73VSCbniIM596rwkn8kOy+fy8RYbL3MC8QedTnigtecmsf4cV8O7nV3h4YmczLXuE6FquiWBQgyflEoT+YMsfRhWV2pV0RJSFr95NBMAwIWN31iWDLK7yhipFMjjuAsXbsY+0/DyqPlW4kfl4YwOIpw47ozNiLGZf6HQq7E0i3wcWdrCcufBcjNF4niW3jB9XyZQ8GVmtfjwTrna7RX0ULVHtmO/zgVc5GRFKbeRRsECgYEAx+ensm/4KlfediHN2D7p0uTRxl5z0N7eqkiL4D4d7ymRVnWWrZjkz90bF3YPIRWnC1hnjAHO09DMOmZPp+CNxY0Dk4CLtWqVzrHCWJlAvJvl6qG1NBgB9OTqpE2RxflXO2hPvVEUD90ziypY35A4ZISqhjG12QfUN+uv/y92t+kCgYEAtepFITDIuFXn7qaO0lPIIGkIBa/xXYPDC5b29dpmVbGcoTk9v2/pJ3JBzEPyGEih7AyWFK2rYgSRpYhro1PCgXRMkKraSt66bGkK8MUmoCXlYc0Cluqw8vDsuyRqTSPkxFwat6TzuQmxZbxX2p61KVrSXgpPhkyWhs0buH9GLusCgYEAsUG4cYDXjLRdjmJrJFSlAVvkpwEZsRvuVQ/+99gcsvUo6oFaGpR4T9i/LQ6CW9PXSzgYmQ0BWNDMRvxxpWp4S7O+eAyD1VmtfJoium0p+hRCysqY4phnI7/YT9h4ahOuRf84taYvI+IA0mW6aIJ5fqgkjNmHZeqLQwq6BI0RuAECgYB0I0xfFDYQ+UdJJSypOrPZfTSR7PG7MhOjoo2oB/atXucQRusU/O1tMZSwQ/CbcENv39kw+m8f9KrHc4DElQTogMcg1PLoOanq7GT/sd4nAAqhlbDBiLPPZeC82VLETNYQRn0IIVc4GugWe1fbStd9v23ue8aphtvS07+O2jKEYQKBgQDE8hlqRbkhj/dhObwfui8YekRU+SeThxWvzSxkZcksZ4w+HcvXZxmlaCPHegssMwrg/QVQaIyTA3BYxLB/46vnD1CnNxnl5BCyePP5vMUudCxh06PTcYlevc+GTfpZahhBXck7SR6dy8tAE/bm7FqtBKAv0QpxThnkG7EZWP2ihQ=='
ALIPAY_PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwy7Xzzm9XnT3Clb2wGmO5O/N1/jpiEgIVomCYiFJJCvADlMdPuVcFaRPYMDj2cE6f2w+MiJQucTazpAbOxC0PQMwcjfFjENVvk0ZfuJwWLQI0bOdbiCN79iaPstjqHgrSFKbU3njuoFkbKImKCu4YbgiQoq+vXan+M80QLhVafMmIqa0jDOBLpqF3iw1xsl0FHxfkRFodHs1obF0cj6Z2qbpzele+LGlkTI9J2l0NIXPDaA0S/w1nsLqN5yfMzExpDxcY+PlQCwSgHPzVqwkQ4dspbEKy+RxJTIbuTJpPNbiVvZwsc3WmxrWzvFH9jk2mr7LccjNbxPVOwOIoJLMCwIDAQAB'
