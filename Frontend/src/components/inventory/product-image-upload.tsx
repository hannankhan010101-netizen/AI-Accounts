"use client";

import Image from "next/image";
import { useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { attachmentsApi } from "@/lib/api/tenant";

type ProductImageUploadProps = {
  productId: string | null;
  attachmentId?: string | null;
  onUploaded?: (attachmentId: string) => void;
  onRemoved?: () => void;
  disabled?: boolean;
};

export function ProductImageUpload({
  productId,
  attachmentId,
  onUploaded,
  onRemoved,
  disabled,
}: ProductImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [previewId, setPreviewId] = useState<string | null>(attachmentId ?? null);

  const upload = useMutation({
    mutationFn: async (file: File) => {
      if (!productId) throw new Error("Save the product before uploading an image");
      return attachmentsApi.upload("product", productId, file);
    },
    onSuccess: (res) => {
      const id = res.result.id as string;
      setPreviewId(id);
      onUploaded?.(id);
      if (inputRef.current) inputRef.current.value = "";
    },
  });

  const remove = useMutation({
    mutationFn: async () => {
      if (!previewId) return;
      await attachmentsApi.delete(previewId, "product");
    },
    onSuccess: () => {
      setPreviewId(null);
      onRemoved?.();
    },
  });

  const imageUrl = previewId ? attachmentsApi.productImageUrl(previewId) : null;

  return (
    <div className="space-y-3">
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) upload.mutate(file);
        }}
      />
      {imageUrl ? (
        <div className="relative h-40 w-40 overflow-hidden rounded-lg border border-border bg-canvas">
          <Image
            src={imageUrl}
            alt="Product"
            fill
            className="object-cover"
            unoptimized
          />
        </div>
      ) : (
        <div className="flex h-40 w-40 items-center justify-center rounded-lg border border-dashed border-border bg-canvas text-xs text-fg-muted">
          No image
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={disabled || upload.isPending || !productId}
          onClick={() => inputRef.current?.click()}
        >
          {upload.isPending ? "Uploading…" : "Upload image"}
        </Button>
        {previewId ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={disabled || remove.isPending}
            onClick={() => remove.mutate()}
          >
            Remove
          </Button>
        ) : null}
      </div>
      {!productId ? (
        <p className="text-xs text-fg-muted">Save the product first, then upload an image.</p>
      ) : null}
      {upload.isError ? (
        <p className="text-sm text-status-danger">{(upload.error as Error).message}</p>
      ) : null}
    </div>
  );
}
