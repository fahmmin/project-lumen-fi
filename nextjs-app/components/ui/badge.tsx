import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
    "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white focus:ring-offset-2",
    {
        variants: {
            variant: {
                default: "border-transparent bg-black dark:bg-white text-white dark:text-black",
                secondary: "border-transparent bg-gray-100 dark:bg-gray-900 text-black dark:text-white",
                outline: "text-black dark:text-white border-black dark:border-white",
                success: "border-transparent bg-white dark:bg-black text-black dark:text-white border border-black dark:border-white",
                warning: "border-transparent bg-white dark:bg-black text-black dark:text-white border border-gray-400 dark:border-gray-600",
                error: "border-transparent bg-black dark:bg-white text-white dark:text-black",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
)

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, ...props }: BadgeProps) {
    return (
        <div className={cn(badgeVariants({ variant }), className)} {...props} />
    )
}

export { Badge, badgeVariants }

