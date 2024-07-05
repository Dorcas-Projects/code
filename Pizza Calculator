package pizzaservingcalculator;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class PizzaServingsCalculator extends JFrame {
    private final JPanel line2 = new JPanel();
    private final JLabel sizeLabel = new JLabel("Enter the size of the pizza in inches: ");
    private final JTextField sizeTextField = new JTextField(4);
    private final JButton calculateButton = new JButton("Calculate Servings");
    private final JLabel resultLabel = new JLabel();

    public PizzaServingsCalculator() {
        setTitle("Pizza Servings Calculator");
        setLayout(new GridLayout(4, 1));

        line2.add(sizeLabel);
        line2.add(sizeTextField);

        calculateButton.addActionListener(new CalculateButtonListener());

        add(new JLabel("Pizza Servings Calculator")).setForeground(Color.RED);
        add(line2);
        add(calculateButton);
        add(resultLabel);

        setSize(350, 300);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setVisible(true);
    }

    private class CalculateButtonListener implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            try {
                double size = Double.parseDouble(sizeTextField.getText());
                double servings = Math.pow((size / 8), 2);
                resultLabel.setText(String.format("Number of servings: %.2f", servings));
            } catch (NumberFormatException ex) {
                resultLabel.setText("Invalid input");
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new PizzaServingsCalculator());
    }
}
