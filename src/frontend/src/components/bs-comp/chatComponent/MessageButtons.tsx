import { ThunmbIcon } from "@/components/bs-icons/thumbs";
import { likeChatApi } from "@/controllers/API";
import { useState } from "react";

const enum ThumbsState {
    Default = 0,
    ThumbsUp,
    ThumbsDown
}

export default function MessageButtons({ id, onCopy, data, onUnlike }) {

    const [state, setState] = useState<ThumbsState>(data)
    const [copied, setCopied] = useState(false)

    const handleClick = (type: ThumbsState) => {
        setState(_type => {
            const newType = type === _type ? ThumbsState.Default : type
            // api
            likeChatApi(id, newType);
            return newType
        })
        if (state !== ThumbsState.ThumbsDown && type === ThumbsState.ThumbsDown) onUnlike?.(id)
    }

    const handleCopy = (e) => {
        setCopied(true)
        onCopy()
        setTimeout(() => {
            setCopied(false)
        }, 2000);
    }

    return <div className="flex gap-1">
        <ThunmbIcon
            type='copy'
            className={`cursor-pointer ${copied && 'text-primary hover:text-primary'}`}
            onClick={handleCopy}
        />
        <ThunmbIcon
            type='like'
            className={`cursor-pointer ${state === ThumbsState.ThumbsUp && 'text-primary hover:text-primary'}`}
            onClick={() => handleClick(ThumbsState.ThumbsUp)}
        />
        <ThunmbIcon
            type='unLike'
            className={`cursor-pointer ${state === ThumbsState.ThumbsDown && 'text-primary hover:text-primary'}`}
            onClick={() => handleClick(ThumbsState.ThumbsDown)}
        />
    </div>
};
