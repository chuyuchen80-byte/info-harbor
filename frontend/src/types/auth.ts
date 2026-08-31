/** 认证相关类型：对应后端 core/models/user.py 统一契约（§7）。 */

export interface User {
  id: string
  username: string
  email: string
  role: string
  status: string
  lastLoginAt?: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface CaptchaResponse {
  captcha_id: string
  image_base64: string
}

export interface LoginPayload {
  account: string
  password: string
  captcha_id: string
  captcha_code: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
  captcha_id: string
  captcha_code: string
}
