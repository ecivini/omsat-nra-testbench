(declare-const x0 Real)
(assert (<= 100.0 x0))
(declare-const x1 Real)
(assert (<= 1000.0 x1))
(declare-const x2 Real)
(assert (<= 1000.0 x2))
(declare-const x3 Real)
(assert (<= 10.0 x3))
(declare-const x4 Real)
(assert (<= 10.0 x4))
(declare-const x5 Real)
(assert (<= 10.0 x5))
(declare-const x6 Real)
(assert (<= 10.0 x6))
(declare-const x7 Real)
(assert (<= 10.0 x7))

(assert (<= (- 1.0) (- (+ (/ (* 833.332520 x3) (* x0 x5)) (/ 100.0 x5) (/ (- 83333.333000) (* x0 x5))))))
(assert (<= (- 1.0) (- (+ (/ (* 1250.0 x4) (* x1 x6)) (/ x3 x6) (/ (* (- 1250.0) x3) (* x1 x6))))))
(assert (<= (- 1.0) (- (+ (/ 1250000.0 (* x2 x7)) (/ x4 x7) (/ (* (- 2500.0) x4) (* x2 x7))))))
(assert (<= (- 1.0) (+ (* (- 0.002500) x3) (* (- 0.002500) x5))))
(assert (<= (- 1.0) (+ (* 0.002500 x3) (* (- 0.002500) x4) (* (- 0.002500) x6))))
(assert (<= (- 1.0) (+ (* 0.010000 x4) (* (- 0.010000) x7))))

(minimize
	(+ (* 1.0 x0) (* 1.0 x1) (* 1.0 x2))
)
(check-sat)
(get-objectives)
(exit)

