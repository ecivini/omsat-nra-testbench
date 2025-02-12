(set-logic QF_UFNRA)
(set-option :produce-models true)

(declare-const x Real)
(declare-const c Real)

(assert (>= x (- 5)))
(assert (< )

(minimize x)
(check-sat)
(get-objectives)
(exit)
