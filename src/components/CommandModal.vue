<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useClipboard } from '@vueuse/core'
import type { Command } from '@/types/command'

const props = defineProps<{
  command: Command
}>()

const emit = defineEmits<{
  close: []
}>()

const { copy, copied } = useClipboard()
const highlighted = computed(() => highlightCommand(props.command.command))

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

async function handleCopy() {
  await copy(props.command.command)
}

function highlightCommand(cmd: string) {
  const escaped = cmd.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  return escaped.replace(/(^|\\s)(-[\\w.:/=]+)(?=\\s|$)/g, (_match, space, flag) => {
    return `${space}<span class="text-blue-600 dark:text-blue-300">${flag}</span>`
  })
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 py-10 backdrop-blur-sm"
    role="dialog"
    aria-modal="true"
    @click.self="emit('close')"
  >
    <div class="card-surface relative w-full max-w-3xl p-6">
      <button
        class="absolute right-4 top-4 rounded-full px-3 py-1 text-lg text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
        aria-label="关闭"
        @click="emit('close')"
      >
        ✕
      </button>

      <div class="flex flex-wrap items-start gap-3">
        <span
          class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-500/10 dark:text-blue-200"
        >
          {{ command.category }}
        </span>
        <span v-if="command.sub" class="text-xs text-slate-500 dark:text-slate-400">/ {{ command.sub }}</span>
        <span v-if="command.danger" class="text-sm text-amber-600">⚠️ {{ command.warning || '危险操作' }}</span>
      </div>

      <h2 class="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
        {{ command.scene }}
      </h2>

      <div class="mt-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 font-mono text-sm dark:border-slate-700 dark:bg-slate-900/60">
          <span class="break-words" v-html="highlighted" />
        </div>
        <button class="btn-primary md:w-36" @click="handleCopy">
          {{ copied ? '✓ 已复制' : '复制命令' }}
        </button>
      </div>

      <div class="mt-5 grid gap-4 md:grid-cols-2">
        <div class="rounded-lg bg-slate-100/60 p-4 dark:bg-slate-800/60">
          <div class="text-sm font-semibold text-slate-700 dark:text-slate-200">参数说明</div>
          <p class="mt-2 text-sm text-slate-700 dark:text-slate-300">
            {{ command.params || '—' }}
          </p>
        </div>

        <div class="rounded-lg bg-slate-100/60 p-4 dark:bg-slate-800/60">
          <div class="text-sm font-semibold text-slate-700 dark:text-slate-200">注意事项 / 常见问题</div>
          <p class="mt-2 text-sm text-slate-700 dark:text-slate-300">
            {{ command.notes || '—' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
