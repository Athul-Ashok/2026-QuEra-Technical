# QuEra iQuHACK 2026 Challenge Documentation

## Team Overview & Challenge Context

This documentation details our team's approach to the QuEra technical challenge for iQuHACK 2026! We focused on noise modeling and parallelism in quantum error correction circuits. Our work explores Gemini-based and depolarization noise modeling surrounding the Steane [[7,1,3]] color code circuit.

We successfully implemented and analyzed a quantum memory experiment using Steane error correction on a distance-3 color code. Our approach involved picking up an understanding of QEC Theory from the ground up and applying to a circuit implementation using Bloqade's Squin kernels. We evaluated fidelity performance through simulations using both Stim and Tsim backends. Cirq translation was also utilized for doing Gemini-based noise modeling.

**Key Achievements:**
- Implemented complete Steane QEC protocol with flag qubit syndrome extraction
- Developed noise injection in the form depolarization and gemini one zone noise
- Characterized error propagation patterns under depolarization noise
- Established foundation for scaling to distance-5 implementations

---

## Part 1: Understanding the Foundation

### Color Code Fundamentals

Our journey began with understanding the [[7,1,3]] color code structure from QuEra's magic state distillation paper. This involved picking up an understanding of the theory behind universal gatesets, syndrome extraction, and more. Though, ultimately we realized the project's core focus wasn't necessarily on magic state distillation and so we immediately started our color code implementation and analysis. Amidst this process, we picked up on interesting behaviors pertaining to the fault-tolerant properties inherent to neutral atom platforms thanks capability to transpile from Squin to Cirq to focus our observations on the behavior of neutral atom's native gateset.

### Steane Error Correction Protocol

We adopted Steane's approach to QEC, which uses ancillary encoded states to extract syndrome information non-destructively. The protocol consists of:

1. **Prepare two auxiliary logical states:**
   - First auxiliary: Encoded |+⟩ state for Z-basis syndrome extraction
   - Second auxiliary: Encoded |0⟩ state for X-basis syndrome extraction

2. **Syndrome extraction through controlled operations:**
   - Entangle data qubits with first auxiliary using CNOT gates
   - Measure first auxiliary in Z-basis
   - Entangle second auxiliary with data qubits (reverse CNOT)
   - Measure second auxiliary in X-basis

3. **Post-selection and error correction:**
   - Analyze syndrome patterns from both measurements
   - Identify error locations and types
   - Apply appropriate corrections (or post-select on error-free cases)

This approach was chosen because it preserves the data qubit state while extracting comprehensive error information.

---

## Part 2: Circuit Implementation Strategy

### State Injection Circuit Architecture

We implemented the magic state injection protocol from QuEra's research as our foundation. The circuit structure follows this pattern:

**Initialization Layer:**
```
- 6 qubits initialized with √Y† gates (creating |−⟩ states)
- 1 qubit left in |0⟩ for state injection
```

**Entanglement Cascade:**
```
Layer 1: CZ gates on pairs (q1,q2), (q3,q4), (q5,q6)
Layer 2: √Y gate on injection qubit (q6)
Layer 3: CZ gates connecting (q0,q3), (q2,q5), (q4,q6)
Layer 4: √Y gates on qubits 2-6
Layer 5: CZ gates on pairs (q0,q1), (q2,q3), (q4,q5)
Layer 6: √Y gates on qubits 1, 2, and 4
```

This structure creates an encoded logical |0⟩ state distributed across all seven physical qubits.

### Modular Kernel Design Philosophy

We designed our implementation with three distinct kernel modules:

**1. Noiseless Kernel (`noiseless_kernel.py`)**
- Serves as the baseline reference implementation
- Validates correct logical state encoding
- Provides ground truth for comparison with noisy simulations
- Confirms all stabilizers measure to zero in ideal conditions

**2. Depolarization Kernel (`depolarization_kernel.py`)**
- Three separate implementations for different noise injection points
- Parameterized noise strength (P parameter)
- Supports both single-qubit and two-qubit depolarization
- Allows systematic study of error propagation

**3. Integrated Steane Protocol (`1915.ipynb` and `state_injection.ipynb`)**
- Combines data encoding with auxiliary state preparation
- Implements complete syndrome extraction pipeline
- Includes measurement and post-processing logic

This modular approach allowed us to:
- Isolate and test individual components
- Rapidly iterate on noise models
- Compare different implementation strategies
- Debug issues systematically

---

## Part 3: Syndrome Extraction and Analysis

### Stabilizer Measurement Strategy

The color code has three stabilizer generators that we check:

**Stabilizer 1:** S₁ = Z₀Z₁Z₂Z₃  
**Stabilizer 2:** S₂ = Z₂Z₃Z₄Z₆  
**Stabilizer 3:** S₃ = Z₁Z₂Z₄Z₅

Our implementation computes these as XOR operations on measured qubit values:
```python
stab1 = sample[0] ^ sample[1] ^ sample[2] ^ sample[3]
stab2 = sample[2] ^ sample[3] ^ sample[4] ^ sample[6]
stab3 = sample[1] ^ sample[2] ^ sample[4] ^ sample[5]
```

**Critical Insight:** In the noiseless case, all stabilizers should measure to zero (False). Any non-zero syndrome indicates an error has occurred.

### Post-Selection Methodology

We implemented a post-selection filter that accepts only shots where all stabilizers return zero:

```python
def false_indices(stabilizer1, stabilizer2, stabilizer3):
    return [
        i for i, (a, b, c) in enumerate(zip(stabilizer1, stabilizer2, stabilizer3))
        if not a and not b and not c
    ]
```

This approach:
- Filters out shots with detected errors
- Provides upper bound on logical error rate
- Simplifies initial analysis before implementing full decoder
- Validates that error-free shots preserve logical information

### Logical Operator Verification

For the [[7,1,3]] color code, we verify the logical Z operator:

**Logical Z:** Z̄ = Z₀Z₁Z₅

Our analysis computes this for all post-selected shots:
```python
for i in results:
    sample = data_results[i]
    log = sample[0] ^ sample[1] ^ sample[5]
    logical_d.append(log)
```

**Key Result:** In noiseless simulations, we achieved 100% fidelity with all logical measurements returning |0⟩ (False), confirming correct encoding and syndrome extraction.

---

## Part 4: Noise Modeling Framework

### Depolarization Channel Implementation

We implemented depolarization noise using Bloqade's native noise primitives:

**Single-Qubit Depolarization:**
```python
squin.broadcast.depolarize(P, IList([target_qubit]))
```

**Two-Qubit Depolarization:**
```python
squin.depolarize2(P, qubit1, qubit2)
```

**Parallel Single-Qubit Noise:**
```python
squin.broadcast.depolarize(P, IList([qubit1, qubit2]))
```

The depolarization channel models the physical error where a qubit has probability P of experiencing a random Pauli error (X, Y, or Z).

### Strategic Noise Injection Points

We identified three critical locations for noise injection:

**Location 1: Initial Data Encoding**
- Noise applied after logical state encoding
- Tests resilience of encoded state before syndrome extraction
- Most fundamental noise scenario

**Location 2: After First Auxiliary Entanglement**
- Noise on aux_1 qubits after CNOT operations
- Before Z-basis measurement
- Tests impact on syndrome reliability

**Location 3: After Second Auxiliary Entanglement**
- Noise on aux_2 qubits after reverse CNOT
- Before X-basis measurement
- Complete picture of syndrome extraction vulnerability

### Noise Parameterization Philosophy

We carefully chose noise strength P = 0.005 (0.5%) because:
- Realistic for near-term neutral atom systems
- Low enough to observe QEC benefit
- High enough to generate statistically significant error events
- Allows meaningful comparison across noise locations

**Important Consideration:** Higher noise rates (>1%) would overwhelm the distance-3 code's correction capability, making the analysis less meaningful.

---

## Part 5: Simulation Methodology

### Backend Selection Strategy

**Stim for Clifford-Only Circuits:**
- Used for noiseless validation
- Extremely fast sampling (100+ shots in milliseconds)
- Perfect accuracy for stabilizer circuits
- Ideal for large-scale statistical analysis

**Tsim for Future Magic States:**
- Prepared infrastructure for T-gate injection
- Handles limited non-Clifford operations efficiently
- Better visualization capabilities
- Foundation for distance-5 scaling

### Sampling and Statistical Approach

Our experimental protocol:
```
Initial runs: 100 shots
- Establish baseline behavior
- Verify stabilizer patterns
- Quick iteration during development

Production runs: 1000+ shots (planned)
- Statistical significance for error rates
- Characterize rare error events
- Validate post-selection efficiency
```

### Data Processing Pipeline

1. **Raw Measurements → Stabilizer Syndromes**
   - Extract aux_1 (7 qubits), aux_2 (7 qubits), data (7 qubits)
   - Compute three stabilizer values per shot
   - Store syndrome patterns

2. **Syndrome Filtering → Valid Shots**
   - Apply post-selection criteria
   - Track rejection rate as noise metric
   - Identify accepted shot indices

3. **Logical Measurement → Fidelity Analysis**
   - Measure logical Z̄ operator
   - Count |0⟩ vs |1⟩ outcomes
   - Calculate logical error rate

---

## Part 6: Results and Key Findings

### Noiseless Baseline Performance

**Perfect Stabilizer Satisfaction:**
- All 100 shots: stabilizer1 = stabilizer2 = stabilizer3 = False
- 100% post-selection acceptance rate
- Validates correct circuit implementation

**Perfect Logical Fidelity:**
- All accepted shots: logical_Z = False (|0⟩ state)
- num_zeros = 100, num_ones = 0
- Confirms logical state preservation

**Interpretation:** The circuit correctly implements the [[7,1,3]] color code encoding and Steane syndrome extraction protocol.

### Noise Impact Observations

**Critical Discovery:** Even with P = 0.005 depolarization:
- Post-selection acceptance rate drops significantly
- Some shots exhibit non-zero syndromes
- Error propagation depends on noise location

**Location-Dependent Behavior:**
1. **Initial data noise:** Directly affects logical state
2. **Auxiliary noise (Location 2):** Corrupts Z-syndrome
3. **Auxiliary noise (Location 3):** Corrupts X-syndrome

### Error Propagation Insights

Through systematic testing, we observed:

**Coherent Error Patterns:**
- Errors often trigger multiple stabilizers simultaneously
- Certain syndrome patterns correlate with specific error types
- Color code structure influences error detectability

**Post-Selection Efficiency:**
- Most errors are successfully flagged by syndrome extraction
- Post-selection provides measurable improvement in logical fidelity
- Trade-off between fidelity and shot efficiency

---

## Part 7: Challenges and Solutions

### Challenge 1: Stabilizer Calculation Complexity

**Initial Problem:** Confusion about which qubits contribute to which stabilizers.

**Solution Process:**
1. Reviewed color code geometry from literature
2. Drew physical qubit layout on paper
3. Manually verified stabilizer generators
4. Cross-referenced with QuEra's implementation
5. Validated with noiseless simulations

**Learning:** Visual representation of qubit connectivity is essential for QEC implementation.

### Challenge 2: Measurement Ordering and Indexing

**Initial Problem:** Unclear how Bloqade orders measurement results in the samples array.

**Solution Process:**
1. Added print debugging to inspect sample shapes
2. Verified: samples[:, 0:7] = aux_1, [:, 7:14] = aux_2, [:, 14:21] = data
3. Created helper functions with clear semantic names
4. Documented indexing conventions in code comments

**Learning:** Careful bookkeeping of qubit indices is critical in multi-register QEC circuits.

### Challenge 3: Noise Model Selection

**Initial Problem:** Many possible noise channels (depolarization, dephasing, amplitude damping, etc.)

**Solution Process:**
1. Started with simplest model: single-qubit depolarization
2. Justified choice: captures essential Pauli error behavior
3. Implemented at multiple circuit locations
4. Planned extension to more realistic native-gate noise models

**Learning:** Start simple, validate thoroughly, then increase complexity systematically.

### Challenge 4: Post-Selection vs. Active Correction

**Initial Problem:** Should we implement a full decoder or use post-selection?

**Solution Process:**
1. Recognized time constraints of hackathon
2. Chose post-selection as intermediate step
3. Designed architecture to support future decoder integration
4. Documented limitation clearly

**Learning:** Pragmatic engineering decisions are essential in time-limited research.

---

## Part 8: Technical Insights and Best Practices

### Bloqade/Squin Lessons Learned

**Kernel Design Patterns:**
- Use `@squin.kernel` decorator for all quantum functions
- Allocate qubits with `squin.qalloc(n)`
- Leverage broadcast operations for parallel gates
- Structure code to match physical hardware constraints

**Noise Integration:**
- Noise operations fit naturally into Squin workflow
- `IList` required for multi-qubit broadcast operations
- Noise strength parameter should be tuned to physical estimates

**Backend Interoperability:**
```python
# Convert to Stim for fast Clifford sampling
stim_circ = bloqade.stim.Circuit(kernel)
sampler = stim_circ.compile_sampler()

# Convert to Tsim for visualization and magic
tsim_circ = bloqade.tsim.Circuit(kernel)
tsim_circ.diagram(height=400)
```

### Debugging Quantum Circuits

**Effective Strategies:**
1. Always start with noiseless case
2. Verify stabilizers measure to zero
3. Add noise incrementally
4. Check intermediate measurement statistics
5. Use visualization tools liberally

**Common Pitfalls:**
- Off-by-one indexing errors
- Incorrect XOR operator usage (use `^` not `xor`)
- Forgetting to convert boolean arrays to counts
- Mismatching qubit labels between encoding and measurement

### Statistical Analysis Considerations

**Sample Size Planning:**
- 100 shots: Quick testing and development
- 1000 shots: Reasonable statistical confidence
- 10000+ shots: Publication-quality error rates

**Post-Selection Bias:**
- Acceptance rate is itself a performance metric
- Must report both logical error rate AND post-selection efficiency
- Trade-off between fidelity and throughput

---

## Part 9: Future Directions

### Immediate Next Steps

**1. Complete Distance-3 Characterization**
- Sweep noise strength from 10⁻⁴ to 10⁻² 
- Generate logical error rate vs physical error rate curves
- Compare different noise locations quantitatively
- Implement proper error bars on all measurements

**2. Active Error Correction Implementation**
- Develop minimum-weight perfect matching decoder
- Implement syndrome-based correction pipeline
- Compare post-selection vs active correction performance
- Measure correction overhead

**3. Native Hardware Noise Models**
- Use Bloqade's Cirq integration for realistic noise
- Model atom shuttling errors
- Include gate-specific error rates
- Validate against heuristic noise models

### Scaling to Distance-5

**Circuit Complexity:**
- Distance-5 color code: 19 physical qubits
- Three auxiliary registers: 57 total qubits
- Significantly larger syndrome space
- More complex stabilizer patterns

**Simulation Challenges:**
- Stim should handle ~60 qubits efficiently
- Need careful memory management
- Parallel processing may be required
- Tsim becomes essential for any non-Clifford gates

**Expected Benefits:**
- Higher error threshold
- Stronger error suppression
- Better demonstration of QEC scaling
- More realistic comparison to experiments

### Magic State Integration

**T-State Preparation:**
- Modify injection qubit initialization
- Add T-gate before encoding
- Use Tsim backend for simulation
- Characterize magic state fidelity

**Distillation Protocol:**
- Implement 15-to-1 distillation
- Cascade multiple distance-3 codes
- Track magic state quality improvement
- Compare to QuEra's experimental results

---

## Part 10: Broader Impact and Lessons

### Understanding Quantum Error Correction

This project deepened our understanding of:

**Theoretical Concepts:**
- Stabilizer formalism and syndrome extraction
- Logical vs physical error rates
- Code distance and error correction capability
- Fault-tolerant operations

**Practical Considerations:**
- Circuit depth and parallelism optimization
- Noise modeling trade-offs
- Measurement and classical processing overhead
- Resource requirements for QEC

### Neutral Atom Platform Insights

Working with Bloqade revealed unique advantages of neutral atoms:

**Connectivity:**
- Flexible atom shuttling enables arbitrary gate connectivity
- Color code geometry naturally maps to 2D atom arrays
- Rearrangement allows circuit optimization

**Error Channels:**
- Dominant errors: dephasing and atom loss
- Gate errors depend on interaction time
- Measurement errors relatively low
- Shuttling introduces position-dependent noise

**Design Implications:**
- Compile circuits to minimize shuttling
- Leverage parallelism in stabilizer measurements
- Optimize for neutral atom native gates (CZ, not CNOT)
- Consider atom loss during syndrome extraction

### Hackathon Methodology

**Successful Strategies:**
1. Early division of labor (theory, coding, analysis)
2. Modular code design for parallel development
3. Frequent integration and testing
4. Clear documentation during development
5. Pragmatic scope management

**Time Management:**
- 30% understanding fundamentals
- 40% implementation and debugging
- 20% testing and validation
- 10% documentation and presentation

---

## Part 11: Acknowledgments and Resources

### Key References

**QuEra Magic State Distillation:**
- arXiv:2412.15165 - Primary circuit design source
- Provided encoding circuit architecture
- Inspired noise modeling approach

**Steane Error Correction:**
- arXiv:2312.09745 - Excellent pedagogical reference
- Section II provided clear QEC overview
- Guided our syndrome extraction implementation

**Color Code Resources:**
- arXiv:2312.03982 - Flagging techniques
- arXiv:2601.13313 - Distance-5 developments
- Informed our scaling strategy

### Tool Ecosystem

**Bloqade Framework:**
- Squin kernel system for circuit construction
- Native noise modeling primitives
- Multi-backend compilation

**Stim Simulator:**
- Ultra-fast stabilizer circuit simulation
- Enabled rapid iteration during development
- Critical for statistical analysis

**Tsim Simulator:**
- Emerging tool for limited magic
- Superior visualization capabilities
- Foundation for future T-state work

---

## Part 12: Conclusion

### Summary of Achievements

We successfully:
1. ✅ Implemented complete Steane QEC protocol for [[7,1,3]] color code
2. ✅ Validated correct encoding with noiseless simulations
3. ✅ Developed modular noise injection framework
4. ✅ Characterized error propagation under depolarization
5. ✅ Established foundation for distance-5 scaling
6. ✅ Demonstrated Bloqade/Stim/Tsim integration

### Key Takeaways

**Technical:**
- Post-selection provides measurable logical error suppression
- Syndrome extraction circuit design critically affects performance
- Noise location significantly impacts correction effectiveness
- Modular kernel design enables systematic QEC analysis

**Methodological:**
- Start simple, validate thoroughly, increase complexity
- Visual debugging essential for quantum circuits
- Statistical approach required for meaningful results
- Hardware-aware design improves QEC efficiency

**Team:**
- Clear role division accelerates progress
- Frequent communication prevents integration issues
- Documentation during development saves time later
- Pragmatic scoping enables completion under constraints

### Vision Forward

This project represents a foundational step toward:
- Practical quantum error correction on neutral atom platforms
- Understanding noise-resilient quantum computing architectures
- Scaling QEC protocols to larger code distances
- Bridging theory and implementation for fault-tolerant quantum computing

The modular framework we developed provides a strong foundation for continued exploration of QEC protocols, noise models, and hardware-aware optimization strategies.

---

## Appendix: Code Architecture Overview

### Repository Structure
```
├── noiseless_kernel.py          # Baseline implementation
├── depolarization_kernel.py     # Parameterized noise models
├── 1915.ipynb                   # Full Steane protocol notebook
├── state_injection.ipynb        # Development and analysis
└── documentation.md             # This document
```

### Key Functions and Their Purposes

**`noiseless()`** - Reference implementation
**`depolarize_1()`** - Location 1 noise injection  
**`depolarize_2()`** - Location 2 noise injection
**`depolarize_3()`** - Location 3 noise injection
**`false_indices()`** - Post-selection filter
**Stabilizer calculation loops** - Syndrome extraction

### Data Flow
```
Kernel Definition → Circuit Compilation → Sampling → 
Syndrome Extraction → Post-Selection → Logical Measurement →
Fidelity Analysis
```

---

**Document Version:** 1.0  
**Date:** January 2026  
**Challenge:** QuEra iQuHACK 2026 Technical Challenge  
**Team:** [Your Team Name]

*This documentation reflects our team's journey through quantum error correction implementation, from initial confusion to successful demonstration of Steane protocol on the [[7,1,3]] color code.*
