import { useRef, useState } from 'react'

// Простая запись голоса для вопроса-аудирования. Отдаёт blob через onRecorded.
export default function AudioRecorder({ onRecorded, disabled }) {
  const [recording, setRecording] = useState(false)
  const mr = useRef(null)
  const chunks = useRef([])
  const stream = useRef(null)

  const start = async () => {
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      alert('Нет доступа к микрофону')
      return
    }
    chunks.current = []
    mr.current = new MediaRecorder(stream.current)
    mr.current.ondataavailable = (e) => e.data.size && chunks.current.push(e.data)
    mr.current.onstop = () => {
      const blob = new Blob(chunks.current, { type: 'audio/webm' })
      stream.current.getTracks().forEach((t) => t.stop())
      if (blob.size) onRecorded(blob)
    }
    mr.current.start()
    setRecording(true)
  }

  const stop = () => { mr.current?.stop(); setRecording(false) }

  return (
    <button
      type="button" disabled={disabled}
      onClick={recording ? stop : start}
      className={`px-3 py-2 rounded-lg text-sm font-medium ${
        recording ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-700'
      } disabled:opacity-50`}
    >
      {recording ? '■ Остановить' : '● Записать голос'}
    </button>
  )
}
