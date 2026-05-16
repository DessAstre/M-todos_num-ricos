import tkinter as tk 
from fractions import Fraction
import copy

ANCHO = 9

def f(x):
    return f"{str(x):^{ANCHO}}"

def var(i):
    letras = ["x","y","z","w","v","u","t","s","r"]
    return letras[i]

# ---------- FORMATOS ----------
def mostrar_sistema(M):
    n=len(M)
    t=""
    for i in range(n):
        coef="".join(f(M[i][j]) for j in range(n))
        indep=f(M[i][n])
        t+=f"|{coef}| |{indep}|\n"
    t+="\n"
    return t

def mostrar_cuadrada(M):
    n=len(M)
    t=""
    for i in range(n):
        fila="".join(f(M[i][j]) for j in range(n))
        t+=f"|{fila}|\n"
    t+="\n"
    return t

def mostrar_aumentada(M,n):
    t=""
    for i in range(n):
        izq="".join(f(M[i][j]) for j in range(n))
        der="".join(f(M[i][j]) for j in range(n,2*n))
        t+=f"|{izq}| |{der}|\n"
    t+="\n"
    return t

# ---------- GAUSS COMPLETO ----------
def gauss(A):

    pasos="===== METODO DE GAUSS =====\n\n"
    M=copy.deepcopy(A)
    n=len(M)

    pasos+="Sistema inicial:\n"
    pasos+=mostrar_sistema(M)

    # Eliminación
    for k in range(n-1):

        piv=None
        for i in range(k,n):
            if M[i][k]!=0:
                piv=i
                break

        if piv is None:
            continue

        if piv!=k:
            pasos+=f"Intercambio F{k+1} ↔ F{piv+1}\n\n"
            M[k],M[piv]=M[piv],M[k]
            pasos+=mostrar_sistema(M)

        for i in range(k+1,n):
            factor=M[i][k]/M[k][k]
            pasos+=f"F{i+1}=F{i+1}-({factor})F{k+1}\n\n"
            for j in range(n+1):
                M[i][j]-=factor*M[k][j]
            pasos+=mostrar_sistema(M)

    # Sustitución hacia atrás
    x=[Fraction(0)]*n

    pasos+="SUSTITUCIÓN HACIA ATRÁS:\n\n"

    for i in range(n-1,-1,-1):

        suma=""
        s=Fraction(0)

        for j in range(i+1,n):
            s+=M[i][j]*x[j]
            suma+=f"({M[i][j]})({x[j]}) + "

        if suma!="":
            suma=suma[:-3]

        pasos+=f"{M[i][i]}{var(i)} + {suma} = {M[i][n]}\n"

        x[i]=(M[i][n]-s)/M[i][i]

        pasos+=f"{var(i)} = ({M[i][n]} - {s})/{M[i][i]} = {x[i]}\n\n"

    pasos+="Solución:\n"
    for i in range(n):
        pasos+=f"{var(i)} = {x[i]}\n"

    return pasos

# ---------- GAUSS JORDAN ----------
def jordan(A):

    pasos="===== METODO GAUSS-JORDAN =====\n\n"
    M=copy.deepcopy(A)
    n=len(M)

    pasos+="Sistema inicial:\n"
    pasos+=mostrar_sistema(M)

    fila=0
    for col in range(n):

        piv=None
        for i in range(fila,n):
            if M[i][col]!=0:
                piv=i
                break

        if piv is None:
            continue

        if piv!=fila:
            pasos+=f"Intercambio F{fila+1} ↔ F{piv+1}\n\n"
            M[fila],M[piv]=M[piv],M[fila]
            pasos+=mostrar_sistema(M)

        pivote=M[fila][col]
        pasos+=f"F{fila+1}=(1/{pivote})F{fila+1}\n\n"

        for j in range(n+1):
            M[fila][j]/=pivote

        pasos+=mostrar_sistema(M)

        for i in range(n):
            if i!=fila:
                factor=M[i][col]
                pasos+=f"F{i+1}=F{i+1}-({factor})F{fila+1}\n\n"
                for j in range(n+1):
                    M[i][j]-=factor*M[fila][j]
                pasos+=mostrar_sistema(M)

        fila+=1

    pasos+="Solución:\n"
    for i in range(n):
        pasos+=f"{var(i)} = {M[i][n]}\n"

    return pasos

# ---------- CRAMER (solo 3x3) ----------
def cramer(A, b):

    pasos="\n===== REGLA DE CRAMER =====\n\n"

    if len(A)!=3:
        pasos+="(Solo disponible para 3x3)\n"
        return pasos

    def det3(M):
        return (M[0][0]*M[1][1]*M[2][2] +
                M[0][1]*M[1][2]*M[2][0] +
                M[0][2]*M[1][0]*M[2][1] -
                M[0][2]*M[1][1]*M[2][0] -
                M[0][0]*M[1][2]*M[2][1] -
                M[0][1]*M[1][0]*M[2][2])

    detA=det3(A)

    if detA==0:
        pasos+="No se puede aplicar Cramer (det=0)\n"
        return pasos

    for k in range(3):
        Ak=copy.deepcopy(A)
        for i in range(3):
            Ak[i][k]=b[i]
        pasos+=f"{var(k)} = {det3(Ak)}/{detA} = {Fraction(det3(Ak),detA)}\n"

    return pasos

# ---------- INVERSA GENERAL ----------
def inversa(A, b):

    pasos="===== MATRIZ INVERSA =====\n\n"

    n=len(A)

    M=[]
    for i in range(n):
        fila=A[i][:]+[Fraction(0)]*n
        fila[n+i]=Fraction(1)
        M.append(fila)

    pasos+="Matriz aumentada inicial:\n"
    pasos+=mostrar_aumentada(M,n)

    for col in range(n):

        piv=None
        for i in range(col,n):
            if M[i][col]!=0:
                piv=i
                break

        if piv is None:
            pasos+="❌ La matriz no tiene inversa (pivote cero)\n"
            return pasos

        if piv!=col:
            pasos+=f"Intercambio F{col+1} ↔ F{piv+1}\n\n"
            M[col],M[piv]=M[piv],M[col]
            pasos+=mostrar_aumentada(M,n)

        pivote=M[col][col]
        pasos+=f"F{col+1}=(1/{pivote})F{col+1}\n\n"

        for j in range(2*n):
            M[col][j]/=pivote

        pasos+=mostrar_aumentada(M,n)

        for i in range(n):
            if i!=col:
                factor=M[i][col]
                pasos+=f"F{i+1}=F{i+1}-({factor})F{col+1}\n\n"

                for j in range(2*n):
                    M[i][j]-=factor*M[col][j]

                pasos+=mostrar_aumentada(M,n)

    pasos+="Matriz inversa:\n"
    inv=[]

    for i in range(n):
        fila=[]
        texto=""
        for j in range(n,2*n):
            fila.append(M[i][j])
            texto+=f(M[i][j])
        inv.append(fila)
        pasos+=f"|{texto}|\n"

    pasos+="\n===== SOLUCIÓN (A⁻¹ b) =====\n\n"

    x=[Fraction(0)]*n
    for i in range(n):
        for j in range(n):
            x[i]+=inv[i][j]*b[j]

    for i in range(n):
        pasos+=f"{var(i)} = {x[i]}\n"

    pasos+=cramer(A,b)

    return pasos

# ---------- INTERFAZ ----------
def crear():
    global entradas
    n=int(tam.get())

    for w in frame.winfo_children():
        w.destroy()
    # Encabezados: marcar claramente la matriz A y el vector b
    tk.Label(frame, text="A", font=(None, 10, "bold")).grid(row=0, column=0, columnspan=n, pady=(0,4))
    tk.Label(frame, text="b", font=(None, 10, "bold")).grid(row=0, column=n, pady=(0,4))

    entradas=[]
    for i in range(n):
        fila=[]
        for j in range(n+1):
            e=tk.Entry(frame,width=6)
            # Desplazar las entradas una fila abajo para dejar espacio a los encabezados
            e.grid(row=i+1,column=j,padx=2,pady=2)
            fila.append(e)
        entradas.append(fila)

def obtener():
    M=[]
    for fila in entradas:
        M.append([Fraction(e.get()) for e in fila])
    return M

def obtener_cuad():
    M=[]
    for fila in entradas:
        M.append([Fraction(e.get()) for e in fila[:-1]])
    return M

def mostrar(txt_res):
    txt.delete(1.0,tk.END)
    txt.insert(tk.END,txt_res)

root=tk.Tk()
root.title("MATRICES PRO 🔥")
root.state("zoomed")

top=tk.Frame(root)
top.pack()

tk.Label(top,text="Tamaño").pack(side="left")
tam=tk.Entry(top,width=5)
tam.pack(side="left")
tk.Button(top,text="Crear",command=crear).pack(side="left")

frame=tk.Frame(root)
frame.pack()

bot=tk.Frame(root)
bot.pack()

tk.Button(bot,text="Gauss",width=15,
          command=lambda: mostrar(gauss(obtener()))).pack(side="left")

tk.Button(bot,text="Gauss-Jordan",width=15,
          command=lambda: mostrar(jordan(obtener()))).pack(side="left")

tk.Button(bot,text="Inversa",width=15,
          command=lambda: mostrar(inversa(
              obtener_cuad(),
              [fila[-1] for fila in obtener()]
          ))).pack(side="left")

scroll=tk.Scrollbar(root)
scroll.pack(side="right",fill="y")

txt=tk.Text(root,font=("consolas",12),yscrollcommand=scroll.set)
txt.pack(fill="both",expand=True)

scroll.config(command=txt.yview)

root.mainloop()