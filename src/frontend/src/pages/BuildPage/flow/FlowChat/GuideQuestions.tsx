import { forwardRef, useEffect, useImperativeHandle, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"

// 引导词推荐
const GuideQuestions = forwardRef(({ locked, chatId, onClick }, ref) => {

    const { t } = useTranslation()
    const [questions, setQuestions] = useState([]) // State to hold questions

    useImperativeHandle(ref, () => ({
        updateQuestions(newQuestions) { // Expose this method to the parent
            console.log('newQuestions :>> ', newQuestions);
            setQuestions(newQuestions)
        }
    }))

    useEffect(() => {
        setQuestions([]) // Clear questions when chatId changes
    }, [chatId])

    const words = useMemo(() => {
        if (questions.length < 4) return questions
        // 随机按序取三个
        const res = []
        const randomIndex = Math.floor(Math.random() * questions.length)
        for (let i = 0; i < 3; i++) {
            const item = questions[(randomIndex + i) % (questions.length - 1)]
            res.push(item)
        }
        return res
    }, [questions])

    if (locked || !words.length) return null

    return (
        <div className="relative">
            <div className="absolute left-0 bottom-0">
                <p className="text-gray-950 text-sm mb-2 bg-[rgba(255,255,255,0.8)] rounded-md w-fit px-2 py-1">
                    {t('chat.recommendationQuestions')}
                </p>
                {
                    words.map((question, index) => (
                        <div
                            key={index}
                            className="w-fit bg-[#d4dffa] border-2 border-gray-50 shadow-md text-gray-600 rounded-md mb-1 px-4 py-1 text-sm cursor-pointer"
                            onClick={() => {
                                onClick(question)
                                setQuestions([])
                            }}
                        >
                            {question}
                        </div>
                    ))
                }
            </div>
        </div>
    )
})

export default GuideQuestions
