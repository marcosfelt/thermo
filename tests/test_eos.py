# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2016, Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from numpy.testing import assert_allclose
import pytest
from thermo.eos import *


@pytest.mark.slow
@pytest.mark.sympy
def test_PR_with_sympy():
    # Test with hexane
    from sympy import  Rational, symbols, sqrt, solve, diff, integrate, N

    P, T, V = symbols('P, T, V')
    Tc = Rational('507.6')
    Pc = 3025000
    omega = Rational('0.2975')
    
    X = (-1 + (6*sqrt(2)+8)**Rational(1,3) - (6*sqrt(2)-8)**Rational(1,3))/3
    c1 = (8*(5*X+1)/(49-37*X)) # 0.45724
    c2 = (X/(X+3)) # 0.07780
    
    R = Rational('8.3144598')
    a = c1*R**2*Tc**2/Pc
    b = c2*R*Tc/Pc
    
    kappa = Rational('0.37464')+ Rational('1.54226')*omega - Rational('0.26992')*omega**2
    
    a_alpha = a*(1 + kappa*(1-sqrt(T/Tc)))**2
    PR_formula = R*T/(V-b) - a_alpha/(V*(V+b)+b*(V-b)) - P
    
    
    
    # First test - volume, liquid
    
    T_l, P_l = 299, 1000000
    PR_obj_l = PR(T=T_l, P=P_l, Tc=507.6, Pc=3025000, omega=0.2975)
#    solns = solve(PR_formula.subs({T: T_l, P:P_l}))
#    solns = [N(i) for i in solns]
#    V_l_sympy = float([i for i in solns if i.is_real][0])
    V_l_sympy = 0.00013022208100139964

    assert_allclose(PR_obj_l.V_l, V_l_sympy)

    def numeric_sub_l(expr):
        return float(expr.subs({T: T_l, P:P_l, V:PR_obj_l.V_l}))

    # First derivatives
    dP_dT = diff(PR_formula, T)
    assert_allclose(numeric_sub_l(dP_dT), PR_obj_l.dP_dT_l)

    dP_dV = diff(PR_formula, V)
    assert_allclose(numeric_sub_l(dP_dV), PR_obj_l.dP_dV_l)
    
    dV_dT = -diff(PR_formula, T)/diff(PR_formula, V)
    assert_allclose(numeric_sub_l(dV_dT), PR_obj_l.dV_dT_l)
    
    dV_dP = -dV_dT/diff(PR_formula, T)
    assert_allclose(numeric_sub_l(dV_dP), PR_obj_l.dV_dP_l)
    
    # Checks out with solve as well
    dT_dV = 1/dV_dT
    assert_allclose(numeric_sub_l(dT_dV), PR_obj_l.dT_dV_l)
    
    dT_dP = 1/dP_dT
    assert_allclose(numeric_sub_l(dT_dP), PR_obj_l.dT_dP_l)
    
    # Second derivatives of two variables, easy ones
    
    d2P_dTdV = diff(dP_dT, V)
    assert_allclose(numeric_sub_l(d2P_dTdV), PR_obj_l.d2P_dTdV_l)
    
    d2P_dTdV = diff(dP_dV, T)
    assert_allclose(numeric_sub_l(d2P_dTdV), PR_obj_l.d2P_dTdV_l)
    
    
    # Second derivatives of one variable, easy ones
    d2P_dT2 = diff(dP_dT, T)
    assert_allclose(numeric_sub_l(d2P_dT2), PR_obj_l.d2P_dT2_l)
    d2P_dT2_maple = -506.20125231401374
    assert_allclose(d2P_dT2_maple, PR_obj_l.d2P_dT2_l)

    d2P_dV2 = diff(dP_dV, V)
    assert_allclose(numeric_sub_l(d2P_dV2), PR_obj_l.d2P_dV2_l)
    d2P_dV2_maple = 4.482165856520912834998e+17
    assert_allclose(d2P_dV2_maple, PR_obj_l.d2P_dV2_l)
        
    # Second derivatives of one variable, Hard ones - require a complicated identity
    d2V_dT2 = (-(d2P_dT2*dP_dV - dP_dT*d2P_dTdV)*dP_dV**-2
              +(d2P_dTdV*dP_dV - dP_dT*d2P_dV2)*dP_dV**-3*dP_dT)
    assert_allclose(numeric_sub_l(d2V_dT2), PR_obj_l.d2V_dT2_l)
    d2V_dT2_maple = 1.16885136854333385E-9
    assert_allclose(d2V_dT2_maple, PR_obj_l.d2V_dT2_l)
    
    d2V_dP2 = -d2P_dV2/dP_dV**3
    assert_allclose(numeric_sub_l(d2V_dP2), PR_obj_l.d2V_dP2_l)
    d2V_dP2_maple = 9.10336131405833680E-21
    assert_allclose(d2V_dP2_maple, PR_obj_l.d2V_dP2_l)


    d2T_dP2 = -d2P_dT2*dP_dT**-3
    assert_allclose(numeric_sub_l(d2T_dP2), PR_obj_l.d2T_dP2_l)
    d2T_dP2_maple = 2.564684443971313e-15
    assert_allclose(d2T_dP2_maple, PR_obj_l.d2T_dP2_l)
    
    d2T_dV2 = (-(d2P_dV2*dP_dT - dP_dV*d2P_dTdV)*dP_dT**-2
              +(d2P_dTdV*dP_dT - dP_dV*d2P_dT2)*dP_dT**-3*dP_dV)
    assert_allclose(numeric_sub_l(d2T_dV2), PR_obj_l.d2T_dV2_l)
    d2T_dV2_maple = -291578941281.8895
    assert_allclose(d2T_dV2_maple, PR_obj_l.d2T_dV2_l)
    
    
    # Second derivatives of two variable, Hard ones - require a complicated identity
    d2T_dPdV = -(d2P_dTdV*dP_dT - dP_dV*d2P_dT2)*dP_dT**-3
    assert_allclose(numeric_sub_l(d2T_dPdV), PR_obj_l.d2T_dPdV_l)
    d2T_dPdV_maple = 0.0699417049626260466429
    assert_allclose(d2T_dPdV_maple, PR_obj_l.d2T_dPdV_l)
    
    d2V_dPdT = -(d2P_dTdV*dP_dV - dP_dT*d2P_dV2)*dP_dV**-3
    assert_allclose(numeric_sub_l(d2V_dPdT), PR_obj_l.d2V_dPdT_l)
    d2V_dPdT_maple = -3.772507759880541967e-15
    assert_allclose(d2V_dPdT_maple, PR_obj_l.d2V_dPdT_l)
    
    # Cv integral, real slow
    # The Cv integral is possible with a more general form, but not here
    # The S and H integrals don't work in Sympy at present
    

    
    
def test_PR_quick():
    # Test solution for molar volumes
    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    Vs_fast = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha)
    Vs_slow = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha, quick=False)
    Vs_expected = [(0.00013022208100139953-0j), (0.001123630932618011+0.0012926962852843173j), (0.001123630932618011-0.0012926962852843173j)]
    assert_allclose(Vs_fast, Vs_expected)
    assert_allclose(Vs_slow, Vs_expected)
    
    # Test of a_alphas
    a_alphas = [3.801259426590328, -0.006647926028616357, 1.6930127618563258e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    eos.set_a_alpha_and_derivatives(299, quick=False)
    a_alphas_slow = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_slow)
    
    # PR back calculation for T
    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, V=0.00013022208100139953, P=1E6)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.00013022208100139953, quick=False)
    assert_allclose(T_slow, 299)
    
    
    diffs_1 = [582232.4757941157, -3665180614672.2373, 1.588550570914177e-07, -2.7283785033590384e-13, 6295046.681608136, 1.717527004374129e-06]
    diffs_2 = [-506.2012523140166, 4.482165856521269e+17, 1.1688513685432287e-09, 9.103361314057314e-21, -291578941282.6521, 2.564684443970742e-15]
    diffs_mixed = [-3.772507759880179e-15, -20523303691.115646, 0.06994170496262654]
    departures = [-31134.740290463407, -72.47559475426019, 25.165377505266793]
    known_derivs_deps = [diffs_1, diffs_2, diffs_mixed, departures]
    
    for f in [True, False]:
        main_calcs = eos.derivatives_and_departures(eos.T, eos.P, eos.V_l, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=f)
        
        for i, j in zip(known_derivs_deps, main_calcs):
            assert_allclose(i, j)
    
    
    
    
    
    # Test Cp_Dep, Cv_dep
    assert_allclose(eos.Cv_dep_l, 25.165377505266747)
    assert_allclose(eos.Cp_dep_l, 44.50559908690951)
    
    # Exception tests
    a = GCEOS()
    with pytest.raises(Exception):
        a.solve_T(P=1E6, V=0.001)
        
    with pytest.raises(Exception):
        a.set_a_alpha_and_derivatives(T=300)
        
    with pytest.raises(Exception):
        PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299)
    
    # Integration tests
    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299.,V=0.00013)
    fast_vars = vars(eos)
    eos.set_properties_from_solution(eos.T, eos.P, eos.V, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=False)
    slow_vars = vars(eos)
    [assert_allclose(slow_vars[i], j) for (i, j) in fast_vars.items() if isinstance(j, float)]

    # One gas phase property
    assert 'g' == PR(Tc=507.6, Pc=3025000, omega=0.2975, T=499.,P=1E5).phase

    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    
    B = eos.b*eos.P/R/eos.T
    A = eos.a_alpha*eos.P/(R*eos.T)**2
    D = -eos.T*eos.da_alpha_dT
    
    V = eos.V_l
    Z = eos.P*V/(R*eos.T)

    # Compare against some known  in Walas [2] functions
    phi_walas =  exp(Z - 1 - log(Z - B) - A/(2*2**0.5*B)*log((Z+(sqrt(2)+1)*B)/(Z-(sqrt(2)-1)*B)))
    phi_l_expect = 0.022212524527244357
    assert_allclose(phi_l_expect, eos.phi_l)
    assert_allclose(phi_walas, eos.phi_l)
    
    # The formula given in [2]_ must be incorrect!
#    S_dep_walas =  R*(-log(Z - B) + B*D/(2*2**0.5*A*eos.a_alpha)*log((Z+(sqrt(2)+1)*B)/(Z-(sqrt(2)-1)*B)))
#    S_dep_expect = -72.47559475426013
#    assert_allclose(-S_dep_walas, S_dep_expect)
#    assert_allclose(S_dep_expect, eos.S_dep_l)
    
    H_dep_walas = R*eos.T*(1 - Z + A/(2*2**0.5*B)*(1 + D/eos.a_alpha)*log((Z+(sqrt(2)+1)*B)/(Z-(sqrt(2)-1)*B)))
    H_dep_expect = -31134.740290463407
    assert_allclose(-H_dep_walas, H_dep_expect)
    assert_allclose(H_dep_expect, eos.H_dep_l)


def test_PR78():
    eos = PR78(Tc=632, Pc=5350000, omega=0.734, T=299., P=1E6)
    three_props = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    expect_props = [8.351960066075052e-05, -63764.64948050847, -130.737108912626]
    assert_allclose(three_props, expect_props)
    
    # Test the results are identical to PR or lower things
    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    PR_props = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    eos = PR78(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    PR78_props = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    assert_allclose(PR_props, PR78_props)


def test_PRSV():
    eos = PRSV(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6, kappa1=0.05104)
    three_props = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    expect_props = [0.0001301268694484059, -31698.916002476708, -74.1674902435042]
    assert_allclose(three_props, expect_props)
    
    # Test of a_alphas
    a_alphas = [3.8129831135199463, -0.006976898745266429, 2.0026547235203598e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    eos.set_a_alpha_and_derivatives(299, quick=False)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    
    # PR back calculation for T
    eos = PRSV(Tc=507.6, Pc=3025000, omega=0.2975, V=0.0001301268694484059, P=1E6, kappa1=0.05104)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.0001301268694484059, quick=False)
    assert_allclose(T_slow, 299)
    
    
    # Test the bool to control its behavior
    eos = PRSV(Tc=507.6, Pc=3025000, omega=0.2975, T=406.08, P=1E6, kappa1=0.05104)
    assert_allclose(eos.kappa, 0.7977689278061457)
    eos.kappa1_Tr_limit = True
    eos.__init__(Tc=507.6, Pc=3025000, omega=0.2975, T=406.08, P=1E6, kappa1=0.05104)
    assert_allclose(eos.kappa, 0.8074380841890093)

    with pytest.raises(Exception):
        PRSV(Tc=507.6, Pc=3025000, omega=0.2975, P=1E6, kappa1=0.05104)

def test_PRSV2():
    eos = PRSV2(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6, kappa1=0.05104, kappa2=0.8634, kappa3=0.460)
    three_props = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    expect_props = [0.00013018821346475254, -31496.173493225753, -73.6152580115141]
    assert_allclose(three_props, expect_props)
    
    # Test of PRSV2 a_alphas
    a_alphas = [3.8054176315098256, -0.00687315871653124, 2.3078008060652167e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    eos.set_a_alpha_and_derivatives(299, quick=False)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    
    # PSRV2 back calculation for T
    eos = PRSV2(Tc=507.6, Pc=3025000, omega=0.2975, V=0.00013018821346475254, P=1E6, kappa1=0.05104, kappa2=0.8634, kappa3=0.460)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.00013018821346475254, quick=False)
    assert_allclose(T_slow, 299)

    # Check this is the same as PRSV
    eos = PRSV(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6, kappa1=0.05104)
    three_props_PRSV = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    eos = PRSV2(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6, kappa1=0.05104)
    three_props_PRSV2 = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    assert_allclose(three_props_PRSV, three_props_PRSV2)
    
    with pytest.raises(Exception):
        PRSV2(Tc=507.6, Pc=3025000, omega=0.2975, T=299.) 


def test_VDW():
    eos = VDW(Tc=507.6, Pc=3025000, T=299., P=1E6)
    three_props = [eos.V_l, eos.H_dep_l, eos.S_dep_l]
    expect_props = [0.00022332978038490077, -13385.722837649315, -32.65922018109096]
    assert_allclose(three_props, expect_props)
    
    # Test of a_alphas
    a_alphas = [2.4841036545673676, 0, 0]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    
    # Back calculation for P
    eos = VDW(Tc=507.6, Pc=3025000, T=299, V=0.00022332978038490077)
    assert_allclose(eos.P, 1E6)
    
    # Back calculation for T
    eos = VDW(Tc=507.6, Pc=3025000, P=1E6, V=0.00022332978038490077)
    assert_allclose(eos.T, 299)

    with pytest.raises(Exception):
        VDW(Tc=507.6, Pc=3025000, P=1E6)


    
def test_RK_quick():
    # Test solution for molar volumes
    eos = RK(Tc=507.6, Pc=3025000, T=299., P=1E6)
    Vs_fast = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha)
    Vs_slow = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha, quick=False)
    Vs_expected = [(0.00015189341729751865+0j), (0.0011670650314512406+0.0011171160630875456j), (0.0011670650314512406-0.0011171160630875456j)]
    assert_allclose(Vs_fast, Vs_expected)
    assert_allclose(Vs_slow, Vs_expected)
    
    # Test of a_alphas
    a_alphas = [3.279647547742308, -0.005484360447729613, 2.75135139518208e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    
    # PR back calculation for T
    eos = RK(Tc=507.6, Pc=3025000,  V=0.00015189341729751865, P=1E6)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.00015189341729751865, quick=False)
    assert_allclose(T_slow, 299)
    
    
    diffs_1 = [400451.9103658808, -1773163557098.2456, 2.258403680601321e-07, -5.63963767469079e-13, 4427906.350797926, 2.49717874759626e-06]
    diffs_2 = [-664.0592454189432, 1.5385265309755005e+17, 1.5035170900333218e-09, 2.759679192734741e-20, -130527989946.59952, 1.0340837610012813e-14]
    diffs_mixed = [-7.870472890849004e-15, -10000515150.46239, 0.08069822580205277]
    departures = [-26160.833620674082, -63.01311649400543, 39.8439858825612]
    known_derivs_deps = [diffs_1, diffs_2, diffs_mixed, departures]
    
    for f in [True, False]:
        main_calcs = eos.derivatives_and_departures(eos.T, eos.P, eos.V_l, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=f)
        
        for i, j in zip(known_derivs_deps, main_calcs):
            assert_allclose(i, j)
    
    
    
    
    
    # Test Cp_Dep, Cv_dep
    assert_allclose(eos.Cv_dep_l, 39.8439858825612)
    assert_allclose(eos.Cp_dep_l, 58.57054992395785)
        
    # Integration tests
    eos = RK(Tc=507.6, Pc=3025000, T=299.,V=0.00013)
    fast_vars = vars(eos)
    eos.set_properties_from_solution(eos.T, eos.P, eos.V, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=False)
    slow_vars = vars(eos)
    [assert_allclose(slow_vars[i], j) for (i, j) in fast_vars.items() if isinstance(j, float)]

    # One gas phase property
    assert 'g' == RK(Tc=507.6, Pc=3025000, T=499.,P=1E5).phase



    # Compare against some known  in Walas [2] functions
    eos = RK(Tc=507.6, Pc=3025000, T=299., P=1E6)
    V = eos.V_l
    Z = eos.P*V/(R*eos.T)

    phi_walas = exp(Z - 1 - log(Z*(1 - eos.b/V)) - eos.a/(eos.b*R*eos.T**1.5)*log(1 + eos.b/V))
    phi_l_expect = 0.052632270169019224
    assert_allclose(phi_l_expect, eos.phi_l)
    assert_allclose(phi_walas, eos.phi_l)
    
    S_dep_walas = -R*(log(Z*(1 - eos.b/V)) - eos.a/(2*eos.b*R*eos.T**1.5)*log(1 + eos.b/V))
    S_dep_expect = -63.01311649400542
    assert_allclose(-S_dep_walas, S_dep_expect)
    assert_allclose(S_dep_expect, eos.S_dep_l)
    
    H_dep_walas = R*eos.T*(1 - Z + 1.5*eos.a/(eos.b*R*eos.T**1.5)*log(1 + eos.b/V))
    H_dep_expect = -26160.833620674082
    assert_allclose(-H_dep_walas, H_dep_expect)
    assert_allclose(H_dep_expect, eos.H_dep_l)
    


def test_SRK_quick():
    # Test solution for molar volumes
    eos = SRK(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    Vs_fast = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha)
    Vs_slow = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha, quick=False)
    Vs_expected = [(0.0001473238480377508+0j), (0.0011693498160811246+0.0012837164440753675j), (0.0011693498160811246-0.0012837164440753675j)]
    assert_allclose(Vs_fast, Vs_expected)
    assert_allclose(Vs_slow, Vs_expected)
    
    # Test of a_alphas
    a_alphas = [3.6749726003997565, -0.006994289319882769, 1.8351979227938195e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    
    # PR back calculation for T
    eos = SRK(Tc=507.6, Pc=3025000, omega=0.2975, V=0.0001473238480377508, P=1E6)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.0001473238480377508, quick=False)
    assert_allclose(T_slow, 299)
    
    # Derivatives
    diffs_1 = [491420.1446383679, -2576742077144.926, 1.9071375012545682e-07, -3.880869602238254e-13, 5243460.41825601, 2.034918614774923e-06]
    diffs_2 = [-464.4582107734843, 2.5298381194906086e+17, 1.3552541457017581e-09, 1.4786993572828407e-20, -195377580143.202, 3.913702219626131e-15]
    diffs_mixed = [-5.1956264229676894e-15, -13750611691.659359, 0.06702442345732229]
    departures = [-30917.940322270817, -72.44137873264927, 27.196322213047413]
    known_derivs_deps = [diffs_1, diffs_2, diffs_mixed, departures]
    
    for f in [True, False]:
        main_calcs = eos.derivatives_and_departures(eos.T, eos.P, eos.V_l, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=f)
        
        for i, j in zip(known_derivs_deps, main_calcs):
            assert_allclose(i, j)
    
    # Test Cp_Dep, Cv_dep
    assert_allclose(eos.Cv_dep_l, 27.196322213047466)
    assert_allclose(eos.Cp_dep_l, 46.90431543572955)
        
    # Integration tests
    eos = SRK(Tc=507.6, Pc=3025000, omega=0.2975, T=299.,V=0.00013)
    fast_vars = vars(eos)
    eos.set_properties_from_solution(eos.T, eos.P, eos.V, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=False)
    slow_vars = vars(eos)
    [assert_allclose(slow_vars[i], j) for (i, j) in fast_vars.items() if isinstance(j, float)]

    
    # Compare against some known  in Walas [2] functions
    eos = SRK(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    V = eos.V_l
    Z = eos.P*V/(R*eos.T)
    D = -eos.T*eos.da_alpha_dT
    
    S_dep_walas = R*(-log(Z*(1-eos.b/V)) + D/(eos.b*R*eos.T)*log(1 + eos.b/V))
    S_dep_expect = -72.44137873264924
    assert_allclose(-S_dep_walas, S_dep_expect)
    assert_allclose(S_dep_expect, eos.S_dep_l)
    
    H_dep_walas = eos.T*R*(1 - Z + 1/(eos.b*R*eos.T)*(eos.a_alpha+D)*log(1 + eos.b/V))
    H_dep_expect = -30917.9403223
    assert_allclose(-H_dep_walas, H_dep_expect)
    assert_allclose(H_dep_expect, eos.H_dep_l)

    phi_walas = exp(Z - 1 - log(Z*(1 - eos.b/V)) - eos.a_alpha/(eos.b*R*eos.T)*log(1 + eos.b/V))
    phi_l_expect = 0.02413706401859461
    assert_allclose(phi_l_expect, eos.phi_l)
    assert_allclose(phi_walas, eos.phi_l)


def test_APISRK_quick():
    # Test solution for molar volumes
    eos = APISRK(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    Vs_fast = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha)
    Vs_slow = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha, quick=False)
    Vs_expected = [(0.00014681823858766455+0j), (0.0011696026208061676+0.001304203394096485j), (0.0011696026208061676-0.001304203394096485j)]
    assert_allclose(Vs_fast, Vs_expected)
    assert_allclose(Vs_slow, Vs_expected)
    
    # Test of a_alphas
    a_alphas = [3.727474247064678, -0.0073349099227097685, 1.9482539852821945e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    eos.set_a_alpha_and_derivatives(299, quick=False)
    a_alphas_slow = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_slow)

    # SRK back calculation for T
    eos = APISRK(Tc=507.6, Pc=3025000, omega=0.2975, V=0.00014681823858766455, P=1E6)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.00014681823858766455, quick=False)
    assert_allclose(T_slow, 299)
    # with a S1 set
    eos = APISRK(Tc=514.0, Pc=6137000.0, S1=1.678665, S2=-0.216396, P=1E6, V=7.045692682173252e-05)
    assert_allclose(eos.T, 299)
    eos = APISRK(Tc=514.0, Pc=6137000.0, omega=0.635, S2=-0.216396, P=1E6, V=7.184691383223729e-05)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=7.184691383223729e-05, quick=False)
    assert_allclose(T_slow, 299)

    
    eos = APISRK(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    # Derivatives
    diffs_1 = [507160.19725861016, -2694519535687.8096, 1.8821915764257067e-07, -3.7112367780430196e-13, 5312955.453232907, 1.9717635678142185e-06]
    diffs_2 = [-495.7033432051597, 2.686049371238787e+17, 1.3462136329121424e-09, 1.3729982416974442e-20, -201893579486.30624, 3.80002419401769e-15]
    diffs_mixed = [-4.990227751881803e-15, -14325368140.50364, 0.06593414440492529]
    departures = [-31759.397282361704, -74.38420560550391, 28.946472091343608]
    known_derivs_deps = [diffs_1, diffs_2, diffs_mixed, departures]
    
    for f in [True, False]:
        main_calcs = eos.derivatives_and_departures(eos.T, eos.P, eos.V_l, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=f)
        
        for i, j in zip(known_derivs_deps, main_calcs):
            assert_allclose(i, j)
    
    # Test Cp_Dep, Cv_dep
    assert_allclose(eos.Cv_dep_l, 28.946472091343608)
    assert_allclose(eos.Cp_dep_l, 49.17373456158243)
        
    # Integration tests
    eos = APISRK(Tc=507.6, Pc=3025000, omega=0.2975, T=299.,V=0.00013)
    fast_vars = vars(eos)
    eos.set_properties_from_solution(eos.T, eos.P, eos.V, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=False)
    slow_vars = vars(eos)
    [assert_allclose(slow_vars[i], j) for (i, j) in fast_vars.items() if isinstance(j, float)]

    # Error checking
    with pytest.raises(Exception):
        APISRK(Tc=507.6, Pc=3025000, omega=0.2975, T=299.) 
    with pytest.raises(Exception):
        APISRK(Tc=507.6, Pc=3025000, P=1E6,  T=299.)
    

def test_TWUPR_quick():
    # Test solution for molar volumes
    eos = TWUPR(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    Vs_fast = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha)
    Vs_slow = eos.volume_solutions(299, 1E6, eos.b, eos.delta, eos.epsilon, eos.a_alpha, quick=False)
    Vs_expected = [(0.0001301754975832377+0j), (0.0011236542243270918+0.0012949257976571766j), (0.0011236542243270918-0.0012949257976571766j)]

    assert_allclose(Vs_fast, Vs_expected)
    assert_allclose(Vs_slow, Vs_expected)
    
    # Test of a_alphas
    a_alphas = [3.806982284033079, -0.006971709974815854, 2.3667018824561144e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    eos.set_a_alpha_and_derivatives(299, quick=False)
    a_alphas_slow = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_slow)

    # back calculation for T
    eos = TWUPR(Tc=507.6, Pc=3025000, omega=0.2975, V=0.0001301754975832377, P=1E6)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.0001301754975832377, quick=False)
    assert_allclose(T_slow, 299)

    
    eos = TWUPR(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    # Derivatives
    diffs_1 = [592877.7698667891, -3683686154532.3066, 1.6094687359218388e-07, -2.7146720921640605e-13, 6213230.351611896, 1.6866883037707508e-06]
    diffs_2 = [-708.101408196832, 4.512488462413035e+17, 1.168546207434993e-09, 9.027515426758444e-21, -280283966933.572, 3.397816790678971e-15]
    diffs_mixed = [-3.82370615408822e-15, -20741143317.758797, 0.07152333089484428]
    departures = [-31652.726391608117, -74.1128253091799, 35.189125483239366]
    known_derivs_deps = [diffs_1, diffs_2, diffs_mixed, departures]
    
    for f in [True, False]:
        main_calcs = eos.derivatives_and_departures(eos.T, eos.P, eos.V_l, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=f)
        
        for i, j in zip(known_derivs_deps, main_calcs):
            assert_allclose(i, j)
    
    # Test Cp_Dep, Cv_dep
    assert_allclose(eos.Cv_dep_l, 35.189125483239366)
    assert_allclose(eos.Cp_dep_l, 55.40579090446679)
        
    # Integration tests
    eos = TWUPR(Tc=507.6, Pc=3025000, omega=0.2975, T=299.,V=0.00013)
    fast_vars = vars(eos)
    eos.set_properties_from_solution(eos.T, eos.P, eos.V, eos.b, eos.delta, eos.epsilon, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=False)
    slow_vars = vars(eos)
    [assert_allclose(slow_vars[i], j) for (i, j) in fast_vars.items() if isinstance(j, float)]

    # Error checking
    with pytest.raises(Exception):
        TWUPR(Tc=507.6, Pc=3025000, omega=0.2975, T=299.) 
        
    # Superctitical test
    eos = TWUPR(Tc=507.6, Pc=3025000, omega=0.2975, T=900., P=1E6)
    eos = TWUPR(Tc=507.6, Pc=3025000, omega=0.2975, V=0.0073716980824289815, P=1E6)
    assert_allclose(eos.T, 900)
    
    
    
    