#!/usr/bin/env python
"""Converte AVI para MP4"""
import os
import imageio

avi_files = [
    "cortes/corte_10.avi",
    "cortes/corte_40.avi",
    "cortes/corte_80.avi"
]

for avi in avi_files:
    if os.path.exists(avi):
        mp4 = avi.replace('.avi', '.mp4')
        print(f"[CONVERT] {avi} -> {mp4}")
        
        try:
            # Abre video AVI
            reader = imageio.get_reader(avi)
            writer = imageio.get_writer(mp4, fps=30, codec='libx264', quality=5)
            
            # Copia frames
            for i, frame in enumerate(reader):
                writer.append_data(frame)
                if (i + 1) % 100 == 0:
                    print(f"  [+] {i+1} frames")
            
            writer.close()
            reader.close()
            
            # Deleta AVI
            os.remove(avi)
            print(f"[DONE] {mp4} criado!")
            
        except Exception as e:
            print(f"[ERROR] {e}")

print("\n[OK] Conversao concluida!")
