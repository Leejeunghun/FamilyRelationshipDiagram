import { useState } from 'react'
import { Check, Copy, KeyRound } from 'lucide-react'

import { getOwnerId, setOwnerId } from '@/lib/ownerId'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export function OwnerIdDialog() {
  const [open, setOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [switchTo, setSwitchTo] = useState('')
  const currentId = getOwnerId()

  async function handleCopy() {
    await navigator.clipboard.writeText(currentId)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  function handleSwitch() {
    if (!switchTo.trim()) return
    setOwnerId(switchTo.trim())
    window.location.reload()
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="ghost">
          <KeyRound className="h-4 w-4" />
          내 ID
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>가족관계도 ID</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-4 text-left">
          <div className="flex flex-col gap-1.5">
            <Label>내 ID (로그인 없이 이 값으로 데이터를 구분합니다)</Label>
            <div className="flex gap-2">
              <Input readOnly value={currentId} className="font-mono text-xs" />
              <Button type="button" variant="outline" size="icon" onClick={handleCopy}>
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              이 ID를 다른 사람에게 알려주면, 그 사람이 아래에 붙여넣어 같은 가족관계도를 함께 볼 수 있습니다.
            </p>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="switch-id">다른 ID로 전환</Label>
            <div className="flex gap-2">
              <Input
                id="switch-id"
                placeholder="공유받은 ID 붙여넣기"
                value={switchTo}
                onChange={(e) => setSwitchTo(e.target.value)}
              />
              <Button type="button" variant="outline" onClick={handleSwitch}>
                전환
              </Button>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button onClick={() => setOpen(false)}>닫기</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
