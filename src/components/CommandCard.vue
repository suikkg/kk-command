<script setup lang="ts">
import { computed } from 'vue'
import { useClipboard } from '@vueuse/core'
import { useCommandStore } from '@/stores/command'
import type { Command } from '@/types/command'

const props = defineProps<{
  command: Command
}>()

const emit = defineEmits<{
  open: [command: Command]
}>()

const store = useCommandStore()
const { copy, copied } = useClipboard()

const isFavorite = computed(() => store.favoriteSet.has(props.command.id))
const highlighted = computed(() => highlightCommand(props.command.command))

async function handleCopy() {
  await copy(props.command.command)
}

function highlightCommand(cmd: string) {
  const escaped = cmd.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  return escaped.replace(/(^|\\s)(-[\\w.:/=]+)(?=\\s|$)/g, (_match, space, flag) => {
    return `${space}<span class="text-blue-600 dark:text-blue-300">${flag}</span>`
  })
}
</script>

<template>
  <article
    class="card-surface flex h-full flex-col gap-3 p-4"
    role="button"
    tabindex="0"
    @click="emit('open', command)"
    @keydown.enter.prevent="emit('open', command)"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex flex-wrap items-center gap-2 text-sm">
        <span
          class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700
            dark:bg-blue-500/10 dark:text-blue-200"
        >
          {{ command.category }}
        </span>
        <span v-if="command.sub" class="text-xs text-slate-500 dark:text-slate-400">/ {{ command.sub }}</span>
      </div>
      <button
        class="rounded-full px-2 text-lg leading-none text-amber-500 transition hover:scale-110"
        :aria-pressed="isFavorite"
        aria-label="收藏"
        @click.stop="store.toggleFavorite(command.id)"
      >
        {{ isFavorite ? '★' : '☆' }}
      </button>
    </div>

    <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-50">{{ command.scene }}</h3>

    <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 font-mono text-sm dark:border-slate-700 dark:bg-slate-900/50">
      <span class="break-words leading-relaxed" v-html="highlighted" />
    </div>

    <p v-if="command.params" class="text-sm text-slate-600 dark:text-slate-300">
      {{ command.params }}
    </p>

    <div v-if="command.danger" class="flex items-center gap-2 text-sm text-amber-600">
      <span aria-hidden="true">⚠️</span>
      <span>{{ command.warning || '危险操作，执行前请确认后果' }}</span>
    </div>

    <div class="mt-auto flex gap-2">
      <button class="btn-primary flex-1 text-sm" @click.stop="handleCopy">
        {{ copied ? '✓ 已复制' : '复制' }}
      </button>
      <button class="btn-ghost text-sm" @click.stop="emit('open', command)">详情</button>
    </div>
  </article>
</template>
