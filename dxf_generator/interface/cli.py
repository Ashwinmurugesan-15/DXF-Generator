# Import domain components
from dxf_generator.domain.ibeam import IBeam
from dxf_generator.domain.column import Column

# Import DXF service to save generated files
from dxf_generator.services.dxf_service import DXFService

# Import base validation exception
from dxf_generator.exceptions.base import DXFValidationError


def get_input(prompt, type_=float):
    """Read and validate user input until correct type is entered."""
    while True:
        try:
            return type_(input(prompt))
        except ValueError:
            print("Invalid input, try again.")


def generate_ibeam():
    """Handles I-Beam generation flow (single or batch)."""
    print("\nSelect mode:")
    print("1. Single Beam")
    print("2. Batch Beam")

    mode = input("Enter choice (1/2): ").strip()

    if mode == "1":
        generate_single_ibeam()
    elif mode == "2":
        generate_batch_ibeam()
    else:
        print("Invalid mode.")


def generate_single_ibeam():
    """Generates a single I-Beam DXF."""
    total_depth = get_input("Total Depth (mm): ")
    flange_width = get_input("Flange Width (mm): ")
    web_thickness = get_input("Web Thickness (mm): ")
    flange_thickness = get_input("Flange Thickness (mm): ")

    # Create I-Beam component
    ibeam = IBeam(total_depth, flange_width, web_thickness, flange_thickness)

    # Build output filename
    filename = f"ibeam_{int(total_depth)}x{int(flange_width)}.dxf"

    # Generate and save DXF
    DXFService.save(ibeam, filename)
    print(f" Generated {filename}")


def generate_batch_ibeam():
    """Generates multiple I-Beams with different inputs."""
    count = int(get_input("How many Beams?: ", int))

    for i in range(count):
        print(f"\nBeam {i+1}")
        try:
            # Collect I-Beam parameters
            total_depth = get_input("Total Depth (mm): ")
            flange_width = get_input("Flange Width (mm): ")
            web_thickness = get_input("Web Thickness (mm): ")
            flange_thickness = get_input("Flange Thickness (mm): ")

            # Create I-Beam instance
            ibeam = IBeam(total_depth, flange_width, web_thickness, flange_thickness)

            # Unique filename per I-Beam
            filename = f"ibeam_{i+1}_{int(total_depth)}x{int(flange_width)}.dxf"

            # Save DXF
            DXFService.save(ibeam, filename)
            print(f"Generated {filename}")

        except DXFValidationError as e:
            # Handle validation failure per I-Beam
            print(f" Beam {i+1} failed validation: {e}")


def generate_column():
    """Handles column generation flow (single or batch)."""
    print("\nSelect mode:")
    print("1. Single Column")
    print("2. Batch Column")

    mode = input("Enter choice (1/2): ").strip()

    # Determine number of columns to generate
    count = 1 if mode == "1" else int(get_input("How many columns?: ", int))

    for i in range(count):
        print(f"\nColumn {i+1}")
        try:
            # Collect column dimensions
            width = get_input("Width (mm): ")
            height = get_input("Height (mm): ")

            # Create column component
            column = Column(width, height)

            # Output filename
            filename = f"column_{i+1}_{int(width)}x{int(height)}.dxf"

            # Save DXF
            DXFService.save(column, filename)
            print(f" Generated {filename}")

        except DXFValidationError as e:
            # Handle validation errors
            print(f" Column {i+1} failed validation: {e}")


def run_cli():
    """Main CLI entry point."""
    print("Welcome to DXF Generator")
    print("========================")

    while True:
        print("\nSelect component:")
        print("1. Beam")
        print("2. Column")
        print("q. Quit")

        choice = input("Enter choice: ").strip().lower()

        if choice == "q":
            break
        elif choice == "1":
            generate_ibeam()
        elif choice == "2":
            generate_column()
        else:
            print("Invalid option.")


# Execute CLI only when run directly
if __name__ == "__main__":
    run_cli()


