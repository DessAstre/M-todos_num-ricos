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

# ---------- ANALISIS ----------
def analizar(M):
    n=len(M)
    rc=0
    ra=0
    for fila in M:
        if any(fila[j]!=0 for j in range(n)):
            rc+=1
        if any(fila[j]!=0 for j in range(n+1)):
            ra+=1
    if rc<ra:
        return "incompatible"
    if rc<n:
        return "multiple"
    return "unica"

# ---------- DETERMINANTE ESTRELLA ----------
def determinante_estrella(A):
    pasos="===== DETERMINANTE MÉTODO ESTRELLA =====\n\n"
    if len(A)!=3:
        pasos+="Solo funciona para matriz 3x3\n"
        return pasos
    pasos+="Matriz:\n"
    a=A
    s_pos=a[0][0]*a[1][1]*a[2][2] + a[0][1]*a[1][2]*a[2][0] + a[0][2]*a[1][0]*a[2][1]
    s_neg=a[0][2]*a[1][1]*a[2][0] + a[0][0]*a[1][2]*a[2][1] + a[0][1]*a[1][0]*a[2][2]
    pasos+=f"Determinante = {s_pos} - {s_neg} = {s_pos - s_neg}\n"
    return pasos

# ---------- GAUSS ----------
def gauss(A):
    pasos="===== METODO DE GAUSS =====\n\n"
    M=copy.deepcopy(A)
    n=len(M)

    pasos+="Sistema inicial:\n"
    pasos+=mostrar_sistema(M)

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

    tipo=analizar(M)

    if tipo!="unica":
        pasos+="El sistema tiene solución múltiple\n"
        return pasos

    x=[Fraction(0)]*n
    pasos+="Sustitución hacia atrás:\n\n"

    for i in range(n-1,-1,-1):
        s=Fraction(0)
        terminos=[]
        for j in range(i+1,n):
            s+=M[i][j]*x[j]
            terminos.append(f"({M[i][j]})({var(j)}={x[j]})")
        x[i]=(M[i][n]-s)/M[i][i]

        if terminos:
            suma_texto=" + ".join(terminos)
        else:
            suma_texto="0"

        pasos+=f"{var(i)} = ({M[i][n]} - ({suma_texto})) / ({M[i][i]}) = {x[i]}\n"

# imprimir en orden correcto
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
    piv_col=[]

    for col in range(n):
        piv=None
        for i in range(fila,n):
            if M[i][col]!=0:
                piv=i
                break
        if piv is None:
            continue

        piv_col.append(col)

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

    tipo=analizar(M)
    pasos+="Solución:\n"

    if tipo=="incompatible":
        pasos+="El sistema no tiene solución\n"
        return pasos

    if tipo=="multiple":

        parametros=["k","t","s","r","p"]
        libres=[i for i in range(n) if i not in piv_col]

    # construir expresiones de todas las variables
        soluciones = [""]*n

    # libres
        for idx,l in enumerate(libres):
            soluciones[l] = parametros[idx]

    # dependientes
        for i,col in enumerate(piv_col):
            expr=f"{M[i][n]}"
            for idx,l in enumerate(libres):
                coef=-M[i][l]
                if coef>0:
                    expr+=f" + {coef}{parametros[idx]}"
                elif coef<0:
                    expr+=f" - {abs(coef)}{parametros[idx]}"
            soluciones[col] = expr

    # imprimir en orden x,y,z
        for i in range(n):
            pasos += f"{var(i)} = {soluciones[i]}\n"

        pasos+="\n(Sistema con solución múltiple)\n"
        return pasos

    for i in range(n):
        pasos+=f"{var(i)} = {M[i][n]}\n"

    return pasos

# ---------- INVERSA ----------
def inversa(A):
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
            pasos+="La matriz no tiene inversa\n"
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
    for i in range(n):
        fila="".join(f(M[i][j]) for j in range(n,2*n))
        pasos+=f"|{fila}|\n"

    return pasos

# ---------- INTERFAZ ----------
def crear():
    global entradas
    n=int(tam.get())

    for w in frame.winfo_children():
        w.destroy()

    entradas=[]
    tk.Label(
        frame,
        text="Matriz A y vector b",
        bg="#f4f6fb",
        fg="#1f4e79",
        font=("Arial", 11, "bold"),
    ).grid(row=0,column=0,columnspan=n+1,pady=(0,8))

    tk.Label(
        frame,
        text="A",
        bg="#f4f6fb",
        fg="#5c6b73",
        font=("Arial", 10, "bold"),
    ).grid(row=1,column=0,columnspan=n,pady=(0,6))

    tk.Label(
        frame,
        text="b",
        bg="#f4f6fb",
        fg="#5c6b73",
        font=("Arial", 10, "bold"),
    ).grid(row=1,column=n,pady=(0,6))

    for i in range(n):
        fila=[]
        for j in range(n+1):
            e=tk.Entry(frame,width=6)
            e.grid(row=i+2,column=j,padx=3,pady=3)
            fila.append(e)
        entradas.append(fila)

    for j in range(n):
        tk.Label(frame,text=var(j),bg="#f4f6fb",fg="#5c6b73",font=("Arial", 9, "bold")).grid(row=n+2,column=j,pady=(8,0))
    tk.Label(frame,text="b",bg="#f4f6fb",fg="#5c6b73",font=("Arial", 9, "bold")).grid(row=n+2,column=n,pady=(8,0))

def cargar_ejemplo():
    tam.delete(0, tk.END)
    tam.insert(0, "3")
    crear()

    A = [
        [2, 1, -1],
        [-3, -1, 2],
        [-2, 1, 2],
    ]
    b = [8, -11, -3]

    for i in range(3):
        for j in range(3):
            entradas[i][j].delete(0, tk.END)
            entradas[i][j].insert(0, str(A[i][j]))
        entradas[i][3].delete(0, tk.END)
        entradas[i][3].insert(0, str(b[i]))

def obtener():
    n=len(entradas)
    M=[]
    for i in range(n):
        fila=[]
        for j in range(n+1):
            fila.append(Fraction(entradas[i][j].get()))
        M.append(fila)
    return M

def obtener_cuad():
    n=len(entradas)
    M=[]
    for i in range(n):
        fila=[]
        for j in range(n):
            fila.append(Fraction(entradas[i][j].get()))
        M.append(fila)
    return M

def mostrar(txt_res):
    txt.delete(1.0,tk.END)
    txt.insert(tk.END,txt_res)

def abrir_ventana_procedimiento(titulo, contenido):
    win = tk.Toplevel(root)
    win.title(f"Procedimiento - {titulo}")
    win.geometry("900x650")
    win.configure(bg="#f4f6fb")

    cab = tk.Frame(win, bg="#1f4e79", pady=10)
    cab.pack(fill="x")

    tk.Label(
        cab,
        text=f"Procedimiento - {titulo}",
        bg="#1f4e79",
        fg="white",
        font=("Arial", 16, "bold"),
    ).pack()

    cuerpo = tk.Frame(win, bg="#f4f6fb", padx=12, pady=12)
    cuerpo.pack(fill="both", expand=True)

    barra = tk.Scrollbar(cuerpo)
    barra.pack(side="right", fill="y")

    txt_proc = tk.Text(
        cuerpo,
        font=("Consolas", 11),
        bg="white",
        relief="flat",
        wrap="none",
        yscrollcommand=barra.set,
    )
    txt_proc.pack(fill="both", expand=True)
    txt_proc.insert(tk.END, contenido)
    txt_proc.config(state="disabled")
    barra.config(command=txt_proc.yview)

    botones = tk.Frame(win, bg="#f4f6fb", pady=10)
    botones.pack(fill="x")

    tk.Button(
        botones,
        text="Volver al programa",
        command=win.destroy,
        bg="#3a7ca5",
        fg="white",
        relief="flat",
        padx=12,
    ).pack(side="left", padx=12)

    tk.Button(
        botones,
        text="Cerrar programa",
        command=root.destroy,
        bg="#8b1e3f",
        fg="white",
        relief="flat",
        padx=12,
    ).pack(side="right", padx=12)

    win.transient(root)
    win.grab_set()
    win.focus_set()

def mostrar_en_ventana(titulo, txt_res):
    mostrar(txt_res)
    abrir_ventana_procedimiento(titulo, txt_res)

root=tk.Tk()
root.title("SSELS Exactos")
root.state("zoomed")
root.configure(bg="#f4f6fb")

root.option_add("*Font", "Arial 10")

cabecera=tk.Frame(root,bg="#1f4e79", pady=12)
cabecera.pack(fill="x")

tk.Label(
    cabecera,
    text="SSELS Exactos",
    bg="#1f4e79",
    fg="white",
        font=("Arial", 18, "bold"),
).pack()

tk.Label(
    cabecera,
    text="Métodos de Gauss, Gauss-Jordan, Inversa y Determinante",
    bg="#1f4e79",
    fg="#dbe9f6",
        font=("Arial", 10),
).pack(pady=(4, 0))

top=tk.Frame(root,bg="#f4f6fb", pady=10)
top.pack(fill="x")

tk.Label(top,text="Tamaño del sistema:",bg="#f4f6fb",fg="#1f1f1f").pack(side="left",padx=(16,6))
tam=tk.Entry(top,width=6,justify="center")
tam.pack(side="left")
tk.Button(top,text="Crear matriz",command=crear,bg="#1f4e79",fg="white",relief="flat",padx=10).pack(side="left",padx=8)
tk.Button(top,text="Ejemplo default",command=cargar_ejemplo,bg="#3a7ca5",fg="white",relief="flat",padx=10).pack(side="left",padx=4)

frame=tk.LabelFrame(root,text="Sistema de ecuaciones",bg="#f4f6fb",fg="#1f1f1f",padx=12,pady=12)
frame.pack(fill="x",padx=16,pady=(0,10))

bot=tk.LabelFrame(root,text="Métodos",bg="#f4f6fb",fg="#1f1f1f",padx=12,pady=10)
bot.pack(fill="x",padx=16,pady=(0,10))

tk.Button(bot,text="Gauss",width=15,
          command=lambda: mostrar_en_ventana("Método de Gauss", gauss(obtener()))).pack(side="left")

tk.Button(bot,text="Gauss-Jordan",width=15,
          command=lambda: mostrar_en_ventana("Método de Gauss-Jordan", jordan(obtener()))).pack(side="left")

tk.Button(bot,text="Inversa",width=15,
          command=lambda: mostrar_en_ventana("Matriz Inversa", inversa(obtener_cuad()))).pack(side="left")

tk.Button(bot,text="Det ⭐",width=15,
          command=lambda: mostrar_en_ventana("Determinante Método Estrella", determinante_estrella(obtener_cuad()))).pack(side="left")

scroll=tk.Scrollbar(root)
scroll.pack(side="right",fill="y")

txt=tk.Text(root,font=("Consolas",12),yscrollcommand=scroll.set,bg="white",relief="flat",wrap="none")
txt.pack(fill="both",expand=True,padx=16,pady=(0,16))

scroll.config(command=txt.yview)

tam.insert(0, "3")
crear()
cargar_ejemplo()

root.mainloop()
