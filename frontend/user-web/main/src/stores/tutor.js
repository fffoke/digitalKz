import { defineStore } from 'pinia'
import {
    startTask, getSession, sendMessage, finishSession,
} from '@/services/tutor'

// TurnOut с бэка → форма реплики для стора (история диалога из БД)
function mapServerTurn(t) {
    if (t.role === 'ai') {
        return { id: 'ai-' + t.id, role: 'ai', text: t.text }
    }
    return {
        id: 'u-' + t.id,
        role: 'user',
        audioUrl: t.audio_url,   // абсолютный URL из /uploads/voice
        transcript: t.transcript,
        duration: 0,             // длительность возьмётся из метаданных аудио
        pending: false,
        failed: false,
    }
}

// Стор активной сессии диалога. Держит реплики (turns) и состояния отправки.
// turn: { id, role: 'user'|'ai', text, transcript, audioUrl, pending, failed }
export const useTutorStore = defineStore('tutor', {
    state: () => ({
        session: null,     // { id, status, task }
        turns: [],
        sending: false,    // идёт расшифровка + ответ ИИ
        result: null,      // { task_score, language_score, feedback }
        finishing: false,
    }),

    getters: {
        active: (s) => s.session?.status === 'active',
    },

    actions: {
        reset() {
            this.session = null
            this.turns = []
            this.sending = false
            this.result = null
            this.finishing = false
        },

        // открыть задание → возобновить активную сессию (с историей) или создать новую
        async start(taskId) {
            this.reset()
            const { data } = await startTask(taskId)
            const s = data.session ?? data
            this._applySession(s)
            return this.session
        },

        // подгрузить существующую сессию (например, после перезагрузки)
        async load(sessionId) {
            const { data } = await getSession(sessionId)
            this._applySession(data.session ?? data)
        },

        // разложить ответ бэка (SessionOut) в стор: история диалога из БД
        _applySession(s) {
            this.session = { id: s.id, task_id: s.task_id, status: s.status, task: s.task }
            this.turns = (s.turns ?? []).map(mapServerTurn)
            this.result = s.result ?? null
        },

        // отправить голосовое: оптимистично показываем своё сообщение,
        // затем дополняем расшифровкой и ответом ИИ
        async send(blob, durationSec) {
            const localUrl = URL.createObjectURL(blob)
            const turn = {
                id: 'u-' + Date.now(),
                role: 'user',
                audioUrl: localUrl,
                duration: durationSec,
                transcript: '',
                pending: true,
                failed: false,
            }
            this.turns.push(turn)
            this.sending = true

            try {
                const { data } = await sendMessage(this.session.id, blob)
                turn.transcript = data.transcript ?? ''
                turn.pending = false
                if (data.ai_text) {
                    this.turns.push({ id: 'ai-' + Date.now(), role: 'ai', text: data.ai_text })
                }
            } catch (e) {
                turn.pending = false
                turn.failed = true
                throw e
            } finally {
                this.sending = false
            }
        },

        async finish() {
            this.finishing = true
            try {
                const { data } = await finishSession(this.session.id)
                this.result = data
                if (this.session) this.session.status = 'finished'
                return data
            } finally {
                this.finishing = false
            }
        },
    },
})
