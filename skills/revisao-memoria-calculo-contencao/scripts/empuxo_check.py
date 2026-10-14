#!/usr/bin/env python3
"""Conferência de ordem de grandeza do empuxo de solo.

Compara o empuxo teórico (Rankine, terreno horizontal, paramento vertical)
com as cargas horizontais declaradas em um relatório estrutural.
Não substitui o cálculo do projetista; serve para decidir se vale questionar.

Exemplo (cargas por pilar em tf, espaçamento 2,07 m, altura 5,2 m):
  python3 empuxo_check.py --gamma 18 --phi 35 --H 5.2 \
      --cargas-tf 3.5 3.0 2.5 2.0 1.5 --espacamento 2.07
"""
import argparse
import math

G = 9.81  # kN por tf


def ka(phi_deg):
    return math.tan(math.radians(45 - phi_deg / 2)) ** 2


def k0(phi_deg):
    return 1 - math.sin(math.radians(phi_deg))


def empuxo(K, gamma, H, q=0.0, c=0.0, hw=0.0):
    """Empuxo total por metro (kN/m) e altura do ponto de aplicação (m).

    Parcelas: triângulo do solo, sobrecarga uniforme e água.
    O desconto de coesão é omitido de propósito (conservador).
    """
    e_solo = 0.5 * K * gamma * H ** 2
    e_q = K * q * H
    e_w = 0.5 * 9.81 * hw ** 2
    total = e_solo + e_q + e_w
    if total == 0:
        return 0.0, 0.0
    momento = e_solo * H / 3 + e_q * H / 2 + e_w * hw / 3
    return total, momento / total


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--gamma", type=float, required=True, help="peso específico do solo (kN/m3)")
    p.add_argument("--phi", type=float, required=True, help="ângulo de atrito efetivo (graus)")
    p.add_argument("--H", type=float, required=True, help="altura de solo contido (m)")
    p.add_argument("--q", type=float, default=0.0, help="sobrecarga a montante (kPa)")
    p.add_argument("--hw", type=float, default=0.0, help="altura de água contra a contenção (m)")
    p.add_argument("--cargas-tf", type=float, nargs="*", default=[],
                   help="cargas horizontais pontuais por pilar (tf), somadas")
    p.add_argument("--espacamento", type=float, default=None,
                   help="espaçamento entre eixos de pilares (m), para converter em tf/m")
    a = p.parse_args()

    Ka, K0 = ka(a.phi), k0(a.phi)
    print(f"Ka = {Ka:.3f}   K0 = {K0:.3f}   (phi = {a.phi} graus)")
    for nome, K in (("ativo", Ka), ("repouso", K0)):
        E, z = empuxo(K, a.gamma, a.H, a.q, hw=a.hw)
        print(f"Empuxo {nome:8s}: E = {E:7.1f} kN/m = {E / G:5.2f} tf/m, ponto de aplicação a {z:.2f} m da base")

    if a.cargas_tf and a.espacamento:
        soma = sum(a.cargas_tf)
        por_m_kn = soma * G / a.espacamento
        print(f"\nCargas declaradas: soma {soma:.2f} tf por pilar, espaçamento {a.espacamento} m")
        print(f"  = {por_m_kn:.1f} kN/m = {por_m_kn / G:.2f} tf/m")
        Kg_equiv = 2 * por_m_kn / a.H ** 2
        print(f"  K*gamma equivalente (empuxo triangular, sem sobrecarga): {Kg_equiv:.2f} kN/m3")
        print(f"  K equivalente para gamma = {a.gamma}: {Kg_equiv / a.gamma:.3f}"
              f"   (Ka = {Ka:.3f}, K0 = {K0:.3f})")
        Ea, _ = empuxo(Ka, a.gamma, a.H, a.q, hw=a.hw)
        E0, _ = empuxo(K0, a.gamma, a.H, a.q, hw=a.hw)
        print(f"  Razão carga declarada / empuxo ativo   = {por_m_kn / Ea:.2f}")
        print(f"  Razão carga declarada / empuxo repouso = {por_m_kn / E0:.2f}")
        print("\nLeitura: razão < 1 contra o empuxo de repouso indica carga declarada menor que a de uma "
              "estrutura travada; peça justificativa do tipo de empuxo, da sobrecarga e da água.")


if __name__ == "__main__":
    main()
