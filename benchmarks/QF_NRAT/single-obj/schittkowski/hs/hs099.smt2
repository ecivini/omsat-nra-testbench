(declare-const x0 Real)
(assert (<= 0.0 x0))
(declare-const x1 Real)
(assert (<= 0.0 x1))
(declare-const x2 Real)
(assert (<= 0.0 x2))
(declare-const x3 Real)
(assert (<= 0.0 x3))
(declare-const x4 Real)
(assert (<= 0.0 x4))
(declare-const x5 Real)
(assert (<= 0.0 x5))
(declare-const x6 Real)
(assert (<= 0.0 x6))
(declare-const x7 Real)
(declare-const x8 Real)
(declare-const x9 Real)
(declare-const x10 Real)
(declare-const x11 Real)
(declare-const x12 Real)
(declare-const x13 Real)
(declare-const x14 Real)
(declare-const x15 Real)
(declare-const x16 Real)
(declare-const x17 Real)
(declare-const x18 Real)

(assert (= (+ (* 1.0 x7) (* (- 15625.0) (sin x0))) (- 10000.0)))
(assert (= (+ (* (- 1.0) x7) (* 1.0 x8) (* (- 25.0) x13) (* (- 15625.0) (sin x1))) (- 10000.0)))
(assert (= (+ (* (- 1.0) x8) (* 1.0 x9) (* (- 50.0) x14) (* (- 93750.0) (sin x2))) (- 40000.0)))
(assert (= (+ (* (- 1.0) x9) (* 1.0 x10) (* (- 50.0) x15) (* (- 93750.0) (sin x3))) (- 40000.0)))
(assert (= (+ (* (- 1.0) x10) (* 1.0 x11) (* (- 50.0) x16) (* (- 93750.0) (sin x4))) (- 40000.0)))
(assert (= (+ (* (- 1.0) x11) (* 1.0 x12) (* (- 90.0) x17) (* (- 405000.0) (sin x5))) (- 129600.0)))
(assert (= (+ (* (- 1.0) x12) (* (- 90.0) x18) (* (- 405000.0) (sin x6))) (- 229600.0)))
(assert (= (+ (* 1.0 x13) (* (- 1250.0) (sin x0))) (- 800.0)))
(assert (= (+ (* (- 1.0) x13) (* 1.0 x14) (* (- 1250.0) (sin x1))) (- 800.0)))
(assert (= (+ (* (- 1.0) x14) (* 1.0 x15) (* (- 3750.0) (sin x2))) (- 1600.0)))
(assert (= (+ (* (- 1.0) x15) (* 1.0 x16) (* (- 3750.0) (sin x3))) (- 1600.0)))
(assert (= (+ (* (- 1.0) x16) (* 1.0 x17) (* (- 3750.0) (sin x4))) (- 1600.0)))
(assert (= (+ (* (- 1.0) x17) (* 1.0 x18) (* (- 9000.0) (sin x5))) (- 2880.0)))
(assert (= (+ (* (- 1.0) x18) (* (- 9000.0) (sin x6))) (- 3880.0)))

(minimize
	(- (^ (+ (* 1250.0 (cos x0)) (* 1250.0 (cos x1)) (* 3750.0 (cos x2)) (* 3750.0 (cos x3)) (* 3750.0 (cos x4)) (* 9000.0 (cos x5)) (* 9000.0 (cos x6))) 2.0))
)
(check-sat)
(get-objectives)
(exit)

