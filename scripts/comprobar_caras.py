"""Comprueba que las caras de los jugadores se VEN en TikTok/IG (usuario 07/10: en Walta = Yamal la barra de arriba de
TikTok tapaba la cara de Walta y casi la de Yamal). Detecta caras (OpenCV YuNet) en la imagen final
1080x1920 y exige que cada una quede entera en la franja visible: x 80-880 e y 330-1540 (arriba, hasta y 318, están
"LIVE · Siguiendo · Para ti"; a la derecha, los iconos). Uso: python3 scripts/comprobar_caras.py img.jpg [n_caras]
Sale con código 1 si alguna cara queda fuera o si encuentra menos caras de las esperadas. Guarda img_caras.png con las
cajas dibujadas para mirarla. Necesita: pip install "opencv-python-headless<5" (la 5 ya no trae Haar)."""
import sys
from pathlib import Path
import cv2

X0, X1, Y0, Y1 = 80, 880, 330, 1540


def caras(ruta):
    """YuNet (scripts/modelos/yunet.onnx, opencv_zoo): detecta caras frontales y de perfil con mucha más precisión que
    Haar (que veía caras en el público y se saltaba a Pedro de perfil). Ignora las caras pequeñas del fondo."""
    img = cv2.imread(ruta); h0, w0 = img.shape[:2]
    det = cv2.FaceDetectorYN.create(str(Path(__file__).with_name("modelos") / "yunet.onnx"), "", (w0, h0), 0.75, 0.3, 5000)
    _, res = det.detect(img)
    return img, [tuple(int(v) for v in r[:4]) for r in (res if res is not None else []) if r[2] >= 90]


def main():
    ruta = sys.argv[1]; esperadas = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    img, cs = caras(ruta); mal = 0
    cv2.rectangle(img, (X0, Y0), (X1, Y1), (0, 0, 255), 4)
    for (x, y, w, h) in cs:
        ok = x >= X0 - w * .15 and x + w <= X1 + w * .15 and y >= Y0 and y + h <= Y1
        mal += not ok
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 200, 0) if ok else (0, 0, 255), 6)
        print(f"cara x={x}-{x + w} y={y}-{y + h}: {'OK' if ok else 'TAPADA o cortada (fuera de x 80-880, y 330-1540)'}")
    visibles = len(cs) - mal
    if visibles < esperadas:
        print(f"[!] solo {visibles} cara(s) visibles de {esperadas}: baja la foto (background-position) o hazla más alta")
    cv2.imwrite(ruta.rsplit(".", 1)[0] + "_caras.png", cv2.resize(img, (540, 960)))
    sys.exit(1 if mal or visibles < esperadas else 0)


if __name__ == "__main__":
    main()
