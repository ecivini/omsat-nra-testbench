(set-logic QF_UFNRA)
(set-option :produce-models true)

(declare-const x Real)
(define-fun f ((y Real)) Real (+ 
                (* (- 0.8) (* y y))
                (* (* 0.45 y) 2)
                2.1))

(assert (>= x (- 10)))
(assert (< x 10))

; Minimize f
(minimize (f x))

(check-sat)
(get-objectives)
(get-model)
(exit)
