(declare-const x0 Real)
(assert (<= 0.0 x0))
(declare-const x1 Real)
(assert (<= 0.0 x1))

(assert (<= 700.0 (* x0 x1)))
(assert (<= 0.0 (+ (* 1.0 x1) (* (- 0.008000) (^ x0 2.0)))))
(assert (<= (- 275.0) (+ (* (- 5.0) x0) (^ (+ (- 50.0) x1) 2.0))))

(minimize
	(+ (* 3.811200 x0) (* 6.830600 x1) (+ (* 0.002057 (^ x0 3.0)) (* (- 0.000010) (^ x0 4.0)) (- (* (* 0.030234 x0) x1)) (* (* 0.001281 x1) (^ x0 2.0)) (* (* 0.000000 (^ x0 4.0)) x1) (* (- 0.256450) (^ x1 2.0)) (* 0.003460 (^ x1 3.0)) (* (- 0.000014) (^ x1 4.0)) (/ 28.106000 (+ 1.0 x1)) (* (* 0.000005 (^ x0 2.0)) (^ x1 2.0)) (* (* 0.000000 (^ x0 3.0)) (^ x1 2.0)) (- (* (* 0.000000 (^ x0 3.0)) (^ x1 3.0))) (- (* (* 0.000340 x0) (^ x1 2.0))) (* (* 0.000002 x0) (^ x1 3.0)) (* 2.867300 (exp (* (* 0.000500 x0) x1))) (- (* (* 0.000035 (^ x0 3.0)) x1)) (* (- 0.126940) (^ x0 2.0)) (- 75.196000)))
)
(check-sat)
(get-objectives)
(exit)

