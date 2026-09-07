import path from 'node:path'

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  // GitHub Pages(프로젝트 페이지)는 https://<계정>.github.io/<저장소이름>/ 형태라
  // 빌드 결과물의 경로 기준을 그 하위 경로로 맞춰야 한다. 로컬 개발 서버는
  // 그대로 루트('/')를 쓰도록 build 명령일 때만 적용한다.
  base: command === 'build' ? '/FamilyRelationshipDiagram/' : '/',
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
}))
