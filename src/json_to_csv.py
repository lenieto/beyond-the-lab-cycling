import json
import csv
import os
import math

def calcular_angulo(p1, p2, p3):
    if p1[2] < 0.1 or p2[2] < 0.1 or p3[2] < 0.1:
        return None
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 == 0 or mag2 == 0:
        return None
    cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
    return round(math.degrees(math.acos(cos_angle)), 2)

def extraer_punto(keypoints, indice):
    base = indice * 3
    return (keypoints[base], keypoints[base+1], keypoints[base+2])

json_dir = os.path.expanduser("~/openpose-workdir/OUTPUT/json")
output_csv = os.path.expanduser("~/openpose-workdir/OUTPUT/angulos.csv")

archivos = sorted([f for f in os.listdir(json_dir) if f.endswith("_keypoints.json")])

with open(output_csv, "w", newline="") as csvfile:
    campos = [
        "frame",
        "codo_derecho", "codo_izquierdo",
        "rodilla_derecha", "rodilla_izquierda",
        "cadera_derecha", "cadera_izquierda",
        "hombro_derecho", "hombro_izquierdo"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=campos)
    writer.writeheader()

    for i, archivo in enumerate(archivos):
        with open(os.path.join(json_dir, archivo)) as f:
            data = json.load(f)

        if not data["people"]:
            continue

        kp = data["people"][0]["pose_keypoints_2d"]
        p = {n: extraer_punto(kp, n) for n in range(25)}

        writer.writerow({
            "frame": i,
            "codo_derecho":    calcular_angulo(p[2], p[3], p[4]),
            "codo_izquierdo":  calcular_angulo(p[5], p[6], p[7]),
            "rodilla_derecha": calcular_angulo(p[9], p[10], p[11]),
            "rodilla_izquierda": calcular_angulo(p[12], p[13], p[14]),
            "cadera_derecha":  calcular_angulo(p[1], p[9], p[10]),
            "cadera_izquierda": calcular_angulo(p[1], p[12], p[13]),
            "hombro_derecho":  calcular_angulo(p[1], p[2], p[3]),
            "hombro_izquierdo": calcular_angulo(p[1], p[5], p[6]),
        })

print(f"✓ CSV generado con {len(archivos)} frames")
print(f"✓ Guardado en: {output_csv}")
